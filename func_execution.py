import time
import numpy as np
import json
import os
import logging
import psutil
import multiprocessing
from datetime import datetime
from tqdm import tqdm
from functools import partial

# Logger Ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Tasarım Vektörü Anahtarları
DESIGN_VECTOR_KEYS = [
    "00_colTopo", "01_colSize", "02_colDirec", "03_colEccL", "04_colEccS",
    "05_colSpanTopo", "06_colSpanSize", "07_colSpanEcc",
    "08_beamTopo", "09_beamSize", "10_beamEcc",
    "11_contBeamTopo", "12_slabSize"
]

def get_memory_usage():
    """
    Mevcut işlemin anlık bellek kullanımını hesaplar.

    Bu fonksiyon, işletim sisteminden süreç (process) bilgisini alarak
    RSS (Resident Set Size) değerini okur.

    Returns:
        float: Kullanılan bellek miktarı (MB cinsinden).
    """
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def format_solution_data(solution_list):
    """
    Ham liste formatındaki çözüm vektörünü etiketli bir sözlüğe çevirir.

    Optimizasyon algoritması genelde veriyi ham liste/array olarak işler,
    ancak kaydederken veya görselleştirirken hangi indeksin ne anlama
    geldiğini bilmek gerekir. Bu fonksiyon bu eşleştirmeyi yapar.

    Args:
        solution_list (list or np.ndarray): Tasarım değişkenlerini içeren ham liste.

    Returns:
        dict or None: Anahtarları 'DESIGN_VECTOR_KEYS' olan sözlük.
                      Girdi geçersizse None veya orijinal listeyi döndürebilir.
    """
    if solution_list is None:
        return None
    
    if len(solution_list) != len(DESIGN_VECTOR_KEYS):
        return solution_list 
    
    formatted = {}
    for key, val in zip(DESIGN_VECTOR_KEYS, solution_list):
        if isinstance(val, np.ndarray):
            formatted[key] = val.tolist()
        else:
            formatted[key] = val
    return formatted

def save_to_json(data, filename):
    """
    Verilen veriyi JSON formatında dosyaya kaydeder.

    NumPy veri tiplerini (int64, float64, ndarray) standart Python
    tiplerine dönüştürerek JSON serileştirme hatalarını önler.

    Args:
        data (dict or list): Kaydedilecek veri yapısı.
        filename (str): Dosyanın kaydedileceği yol ve isim.

    Returns:
        None
    """
    def np_encoder(object):
        if isinstance(object, np.generic):
            return object.item()
        if isinstance(object, np.ndarray):
            return object.tolist()
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=np_encoder, indent=4)
    except Exception as e:
        logging.error(f"JSON kayıt hatası: {e}")

def _worker_wrapper(func, static_kwargs, dynamic_args):
    """
    Tek bir optimizasyon koşumunu (run) sarmalayan ve yöneten işçi fonksiyon.

    Bu fonksiyon, multiprocessing havuzu veya seri döngü tarafından çağrılır.
    Hata yakalama, bellek ölçümü, seed atama ve sonuç formatlama işlemlerini yapar.

    Args:
        func (callable): Çalıştırılacak optimizasyon fonksiyonu (örn: optimization_task).
        static_kwargs (dict): Tüm koşumlar için sabit olan parametreler (config vb.).
        dynamic_args (tuple): (seed, run_id) ikilisi.

    Returns:
        dict: İşlem sonucunu içeren yapı:
            {
                "payload": { ...meta veriler, skorlar, hatalar... },
                "best_solution": ...ham en iyi çözüm...
            }
    """
    seed, run_id = dynamic_args
    np.random.seed(seed)
    
    start_time = time.time()
    start_mem = get_memory_usage()
    
    result_payload = {
        "run_id": run_id,
        "seed": seed,
        "status": "pending",
        "error": None,
        "duration": 0,
        "best_score": None,
        "first_iter_score": None,     
        "convergence": None,
        "first_iter_solution": None,  
        "final_solution": None,       
        "metrics": {},
        "visual_path": ""
    }

    try:
        # func -> StructuralOptimizer.run çağrısı
        output = func(seed=seed, run_id=run_id, **static_kwargs)
        
        # Dönüş değerlerini ayıkla
        best_sol = output["best_sol"]
        best_score = output["best_score"]
        history = output["history"]
        first_iter_sol = output.get("first_iter_sol")
        first_iter_score = output.get("first_iter_score")
        
        metrics = output.get("metrics", {})
        visual_path = output.get("visual_path", "")
        
        result_payload["status"] = "success"
        result_payload["best_score"] = best_score
        result_payload["convergence"] = history[-1] if history else None
        
        # Verileri kaydet
        result_payload["first_iter_score"] = first_iter_score
        result_payload["first_iter_solution"] = format_solution_data(first_iter_sol)
        result_payload["final_solution"] = format_solution_data(best_sol)

        result_payload["metrics"] = metrics
        result_payload["visual_path"] = visual_path
        
        # Worker dönüş değeri
        worker_return = {
            "payload": result_payload,
            "best_solution": best_sol
        }
        
    except Exception as e:
        result_payload["status"] = "failed"
        result_payload["error"] = str(e)
        logging.error(f"Run {run_id} failed: {e}")
        worker_return = {"payload": result_payload, "best_solution": None}

    end_time = time.time()
    end_mem = get_memory_usage()
    
    result_payload["duration"] = end_time - start_time
    result_payload["memory_change_mb"] = end_mem - start_mem
    
    return worker_return

def run_optimization(optimization_func, num_runs=10, parallel=False, batch_size=50, output_dir="results", **params):
    """
    Optimizasyon sürecini yöneten ana orkestratör fonksiyon.

    Belirtilen sayıda (num_runs) denemeyi seri veya paralel olarak gerçekleştirir.
    İlerleme çubuğu (tqdm) ile durumu gösterir, sonuçları toplar ve
    detaylı bir JSON raporu oluşturur.

    Args:
        optimization_func (callable): Her bir run için çağrılacak fonksiyon.
        num_runs (int): Toplam kaç kez optimizasyon yapılacağı. Varsayılan: 10.
        parallel (bool): İşlemlerin paralel (multiprocessing) yapılıp yapılmayacağı. Varsayılan: False.
        batch_size (int): Bellek şişmesini önlemek için işlemlerin kaçarlı gruplar halinde yapılacağı. Varsayılan: 50.
        output_dir (str): Sonuçların ve görsellerin kaydedileceği klasör yolu. Varsayılan: "results".
        **params: Optimizasyon fonksiyonuna (worker'a) iletilecek ek parametreler (geoData vb.).

    Returns:
        dict: Tüm süreci özetleyen final raporu (istatistikler, en iyi çözüm, tüm run geçmişi).
    """
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = os.path.join(output_dir, f"history_{timestamp}.json")
    
    visuals_dir = os.path.join(output_dir, "visuals")
    if not os.path.exists(visuals_dir):
        os.makedirs(visuals_dir)
    params["output_dir"] = output_dir
    
    print(f"\n--- Optimizasyon Başlatılıyor: {num_runs} Run ---\n")

    master_seed = np.random.randint(0, 10000)
    np.random.seed(master_seed)
    seeds = np.random.randint(0, 10000000, size=num_runs)
    
    global_best_score = np.inf
    global_best_sol = None
    all_meta_data = []
    success_count = 0
    
    pbar = tqdm(total=num_runs, desc="🚀 İlerleme", unit="run")
    
    tasks = list(zip(seeds, range(1, num_runs + 1)))
    
    for i in range(0, num_runs, batch_size):
        batch_tasks = tasks[i : i + batch_size]
        batch_results = []
        
        worker = partial(_worker_wrapper, optimization_func, params)
        
        if parallel and num_runs > 1:
            cpu_use = max(1, int(multiprocessing.cpu_count() * 0.7))
            with multiprocessing.Pool(processes=cpu_use) as pool:
                batch_results = list(pool.map(worker, batch_tasks))
        else:
            for args in batch_tasks:
                batch_results.append(worker(args))
                
        for res_wrap in batch_results:
            pbar.update(1)
            
            res_payload = res_wrap["payload"]
            best_sol = res_wrap["best_solution"]
            
            all_meta_data.append(res_payload)
            
            if res_payload["status"] == "success":
                success_count += 1
                score = res_payload["best_score"]
                
                if score < global_best_score:
                    global_best_score = score
                    global_best_sol = best_sol
                    
                    formatted_temp = format_solution_data(global_best_sol)
                    save_to_json(formatted_temp, os.path.join(output_dir, "temp_best_sol.json"))
                    
                    pbar.set_postfix({"Enİyi": f"{global_best_score:.4f}"})

        del batch_results
        
    pbar.close()

    valid_scores = [m["best_score"] for m in all_meta_data if m["best_score"] is not None]
    durations = [m["duration"] for m in all_meta_data]
    
    stats = {
        "total_runs": num_runs,
        "success_count": success_count,
        "success_rate": (success_count / num_runs) * 100,
        "avg_time": np.mean(durations) if durations else 0,
        "best_score": np.min(valid_scores) if valid_scores else None,
        "std_dev": np.std(valid_scores) if valid_scores else None
    }
    
    formatted_best_sol = format_solution_data(global_best_sol)
    
    final_report = {
        "timestamp": timestamp,
        "run_statistics": stats,
        "best_solution_data": formatted_best_sol,
        "individual_runs": all_meta_data
    }
    
    save_to_json(final_report, history_file)
    print(f"\nRapor: {history_file}")
    
    return final_report