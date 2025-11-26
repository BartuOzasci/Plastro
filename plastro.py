# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# --- MODÜL İMPORTLARI ---
import func_misc as misc
import read_DXF as dxfReader
import read_XLS as xlsReader
import build_data_geo as buildGeo
import build_data_span_walls as buildWalls
import build_data_geo_symmetry as buildSym
import build_data_struct as buildStruct
import build_data_fitness as buildFit
import build_data_repair as buildRepMask
import build_data_cont_lines as buildContLines
import build_data_contBeam as buildContBeam
import build_data_penalty as buildPenalty
import func_optimization_loop as optLoop
import func_execution as execManager
import draw_basic_geometry as drawGeo
import draw_struct_members as drawMembers

def initialize_system(dxf_path, xls_path):
    """
    Sistemi başlatır, dosyaları okur ve tüm statik proje verilerini hazırlar.

    Bu fonksiyon, optimizasyon süreci boyunca değişmeyecek olan geometrik verileri,
    kesit özelliklerini, komşuluk ilişkilerini ve onarım maskelerini hesaplar.

    Args:
        dxf_path (str): .dxf dosyasının tam yolu.
        xls_path (str): .xlsx dosyasının tam yolu.

    Returns:
        dict: Optimizasyon için gerekli tüm statik verileri içeren sözlük.
              (geoData, xls, contBeam, slabProp, fit_span, fit_node, repairMask, colSecProp, dxf)
    """
    print("\n" + "="*60)
    print(f"{'PLASTRO: YAPISAL OPTİMİZASYON SİSTEMİ':^60}")
    print("="*60 + "\n")

    if not os.path.exists(dxf_path) or not os.path.exists(xls_path):
        print("HATA: Giriş dosyaları (DXF veya XLS) bulunamadı.")
        sys.exit(1)

    # 1. Dosya Okuma
    dxf = misc.measure_exec_time("1a. DXF OKUMA", dxfReader.read_DXF, dxf_path)
    xls = misc.measure_exec_time("1b. XLS OKUMA", xlsReader.read_XLS, xls_path)

    # 2. Geometri ve Duvarlar
    geoData = misc.measure_exec_time("2.  GEODATA", buildGeo.build_data_geo,
        dxf["axes"], dxf["basePol_points"], dxf["floorPol_points"], dxf["areas_points"])

    spanWalls = misc.measure_exec_time("3.  WALLS", buildWalls.build_data_span_walls,
        geoData["spans"], geoData["nodes"], dxf["walls"])

    # 3. Simetri ve Kesit Özellikleri
    # Not: symData hesaplanıyor ancak şu an aktif kullanılmıyor olabilir, yine de tutuyoruz.
    symData = misc.measure_exec_time("4.  SYMDATA", buildSym.build_data_geo_symmetry,
        geoData["floorPol"], geoData["nodes"], geoData["axNod"],
        geoData["spans"], geoData["areas"])

    colSecProp = misc.measure_exec_time("5a. COL SEC PROP", buildStruct.calc_colSecProp, xls["colSec"])
    slabProp   = misc.measure_exec_time("5b. SLAB PROP", buildStruct.calc_slabProp, geoData, dxf, xls)

    # 4. Fitness Ön Hazırlığı
    fit_span = misc.measure_exec_time("6a. FIT SPAN", buildFit.build_fitness_span_in_area,
        geoData["spanLen"], geoData["spanInArea"], slabProp["importance"])
    fit_node = misc.measure_exec_time("6b. FIT NODE", buildFit.build_fitness_node_in_area,
        geoData["nodInArea"], slabProp["importance"])

    # 5. Onarım ve Süreklilik Analizi
    repairMask = misc.measure_exec_time("7.  REPAIR MASKS", buildRepMask.build_data_repair,
        geoData, slabProp, spanWalls, xls, dxf)

    contLines = misc.measure_exec_time("8a. CONT LINES", buildContLines.build_data_cont_lines,
        geoData["axNod"], geoData["axesDirection"], geoData["nodMat"], geoData["spanLen"],
        maxJumpLength=xls["colSpanLenLim"]["max"], maxJumpCount=1)

    contBeam = misc.measure_exec_time("8b. CONT BEAMS", buildContBeam.build_contBeam,
        geoData, contLines, xls, repairMask, fit_span)

    # Tüm verileri bir paket halinde döndür
    return {
        "geoData": geoData,
        "xls": xls,
        "dxf": dxf,
        "contBeam": contBeam,
        "slabProp": slabProp,
        "fit_span": fit_span,
        "fit_node": fit_node,
        "repairMask": repairMask,
        "colSecProp": colSecProp
    }

def optimization_task(seed, run_id, output_dir, pop_size, max_iter, **context):
    """
    Tek bir optimizasyon koşumunu (run) gerçekleştiren işçi fonksiyonu.
    
    Bu fonksiyon, 'execManager' tarafından çağrılır. Statik verileri 'context'
    içinden alır, optimizasyonu çalıştırır ve sonuçları analiz eder.

    Args:
        seed (int): Rastgele sayı üreteci için tohum değeri.
        run_id (int): Koşum kimlik numarası.
        output_dir (str): Çıktıların kaydedileceği dizin.
        pop_size (int): Popülasyon büyüklüğü.
        max_iter (int): Maksimum iterasyon sayısı.
        **context: 'initialize_system' tarafından üretilen statik veri paketi
                   (geoData, xls, contBeam vb. anahtarları içerir).

    Returns:
        dict: En iyi çözüm, skorlar, tarihçe, metrikler ve görsel yolunu içeren sonuç paketi.
    """
    # Veri paketini aç
    geoData = context["geoData"]
    xls = context["xls"]
    contBeam = context["contBeam"]
    slabProp = context["slabProp"]
    fit_span = context["fit_span"]
    fit_node = context["fit_node"]
    repairMask = context["repairMask"]
    
    # Paralel işleme güvenliği için backend ayarla
    plt.switch_backend('Agg') 

    # 1. Optimizasyon Başlatma
    # Not: run() metodu artık initial ve final penalty değerlerini de döndürüyor (Turn 2)
    optimizer = optLoop.StructuralOptimizer(
        geoData, xls, contBeam, slabProp, 
        fit_span, fit_node, repairMask
    )
    np.random.seed(seed)
    best_sol, best_obj, history, init_pen, final_pen = optimizer.run(pop_size=pop_size, max_iter=max_iter)

    # 2. Detaylı Metrik Hesaplama
    # A. Penalty Detayları (Final ve Initial)
    penalty_dict_final = {
        "beam_length_viol": float(final_pen[0]),
        "beam_dist_viol": float(final_pen[1]),
        "col_dist_viol": float(final_pen[2]),
        "beam_free_end_len": float(final_pen[3])
    }
    
    # B. Fitness Detayları
    fitness_vals = buildFit.build_data_fitness(best_sol, geoData, contBeam, fit_span, fit_node)
    fitness_dict = {
        "span_area_cost": float(fitness_vals[0]),
        "node_area_cost": float(fitness_vals[1]),
        "standalone_beam_cost": float(fitness_vals[2]),
        "crossing_beam_cost": float(fitness_vals[3])
    }

    # 3. Sonuç Görselleştirme
    visuals_path = os.path.join(output_dir, "visuals")
    if not os.path.exists(visuals_path):
        os.makedirs(visuals_path, exist_ok=True)
        
    filename = f"run_{run_id}_seed_{seed}.png"
    full_path = os.path.join(visuals_path, filename)

    try:
        # Yapısal veri oluştur
        colSecProp = context["colSecProp"] # Çizim için gerekli
        dxf = context["dxf"]               # Çizim için gerekli
        structData = buildStruct.build_data_struct(best_sol, xls, geoData, colSecProp, slabProp)
        
        # Çizim
        fig, ax = drawGeo.draw_basic_geometry(
            dxf["axes"], geoData["nodes"], geoData["spans"], geoData["areas"], geoData["spansG"], geoData["areasG"], 
            action="none",
            components=["axes", "nodes", "areas"]
        )
        drawMembers.draw_member_groups(ax, structData, member_groups=["col", "colSpan", "beam", "slab"])
        
        # Başlık ekle
        ax.set_title(f"Run {run_id} | Score: {best_obj:.4f}", fontsize=10)
        
        # Kaydet ve kapat
        fig.savefig(full_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
    except Exception as e:
        print(f"Görselleştirme hatası (Run {run_id}): {e}")
        full_path = None

    # 4. Sonuç Döndürme
    # Not: Initial penalty değerleri raporda kullanılmak üzere 'metrics' altına eklenebilir
    # veya ayrı bir anahtar olarak dönebilir, ancak standart yapı 'metrics' kullanır.
    return {
        "best_sol": best_sol,
        "best_score": best_obj,
        "history": history,
        "first_iter_sol": None, # İsteğe bağlı: optimize edilmiş ilk çözüm buraya eklenebilir
        "first_iter_score": None, # İsteğe bağlı
        "metrics": {
            "fitness": fitness_dict,
            "penalty": penalty_dict_final
        },
        "visual_path": full_path
    }

def visualize_final_result(results, context):
    """
    Tüm denemeler sonucunda elde edilen en iyi çözümü ekrana çizer.

    Args:
        results (dict): 'execManager.run_optimization' çıktısı.
        context (dict): Statik veri paketi.

    Returns:
        None
    """
    if results["best_solution_data"] is not None:
        print("\n" + "-"*40)
        print("🏆 EN İYİ SONUÇ GÖRSELLEŞTİRİLİYOR...")
        print("-"*40)
        
        # Veri paketini aç
        geoData = context["geoData"]
        xls = context["xls"]
        dxf = context["dxf"]
        colSecProp = context["colSecProp"]
        slabProp = context["slabProp"]

        # 1. Veri Tipi Dönüşümü
        best_sol_data = results["best_solution_data"]
        
        if isinstance(best_sol_data, dict):
            sorted_keys = sorted(best_sol_data.keys())
            best_sol_list = [np.array(best_sol_data[k]) for k in sorted_keys]
        else:
            best_sol_list = best_sol_data

        # 2. Yapısal Veriyi Oluştur
        structData = buildStruct.build_data_struct(
            best_sol_list, xls, geoData, colSecProp, slabProp)

        # 3. Temel Geometriyi Çiz
        fig, ax = drawGeo.draw_basic_geometry(
            dxf["axes"], geoData["nodes"], geoData["spans"], geoData["areas"], geoData["spansG"], geoData["areasG"], 
            action="none",
            components=["axes", "nodes", "areas", "axis labels", "span labels", "area labels"]
        )

        # 4. Yapı Elemanlarını Çiz ve Göster
        drawMembers.draw_struct_members(
            (fig, ax), 
            structData, 
            action="show",
            member_groups=["col", "colSpan", "beam", "slab"]
        )
    else:
        print("\n❌ Geçerli bir çözüm bulunamadı veya tüm denemeler başarısız oldu.")

if __name__ == "__main__":
    # 1. Ayarlar
    script_path = os.path.dirname(os.path.abspath(__file__))
    fileNameDXF = os.path.join(script_path, '_test.dxf')
    fileNameXLS = os.path.join(script_path, '_test.xlsx')
    
    CONFIG = {
        "num_runs": 1,           # Toplam deneme sayısı
        "parallel": False,       # Paralel işleme
        "batch_size": 10,
        "output_dir": "plastro_results",
        "pop_size": 30,
        "max_iter": 1000
    }

    # 2. Sistemi Başlat (Statik Verileri Yükle)
    static_context = initialize_system(fileNameDXF, fileNameXLS)

    # 3. Optimizasyonu Çalıştır
    # Not: static_context içindeki her şey kwargs olarak optimization_task'a gider
    final_results = execManager.run_optimization(
        optimization_func=optimization_task,
        num_runs=CONFIG["num_runs"],
        parallel=CONFIG["parallel"],
        batch_size=CONFIG["batch_size"],
        output_dir=CONFIG["output_dir"],
        pop_size=CONFIG["pop_size"],
        max_iter=CONFIG["max_iter"],
        **static_context 
    )

    # 4. Sonucu Göster
    visualize_final_result(final_results, static_context)