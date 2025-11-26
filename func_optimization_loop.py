import numpy as np
import copy
import time

# Proje modülleri
import func_optimization as funcOpti
import build_data_repair as buildRepMask
import build_data_od_repair as buildODRepair
import build_data_penalty as buildPenalty
import build_data_fitness as buildFit

class StructuralOptimizer:
    """
    Yapısal optimizasyon sürecini başlatan ve yöneten ana sınıf.

    Bu sınıf, geometrik verileri, kesit özelliklerini ve kısıtlamaları alarak
    JAYA algoritması tabanlı bir optimizasyon döngüsü kurar. Aday çözümlerin
    üretilmesi, onarılması, cezalandırılması ve seçilmesi süreçlerini koordine eder.
    """

    def __init__(self, geoData, xls, contBeam, slabProp, fitness_span_in_area, fitness_node_in_area, repairMask):
        """
        Optimizer sınıfını başlatır ve gerekli statik verileri yükler.

        Args:
            geoData (dict): Düğümler, akslar ve açıklıklar gibi geometrik veriler.
            xls (dict): Excel'den okunan kesit (profil) ve kısıtlama verileri.
            contBeam (list): Sürekli kiriş hatlarının listesi.
            slabProp (dict): Döşeme (slab) özellikleri ve parametreleri.
            fitness_span_in_area (np.array): Alan içi açıklık maliyet matrisi (Fitness hesabı için).
            fitness_node_in_area (np.array): Alan içi düğüm maliyet vektörü (Fitness hesabı için).
            repairMask (dict): Geçersiz elemanları düzeltmek için kullanılan onarım maskeleri.
        """
        self.geoData = geoData
        self.xls = xls
        self.contBeam = contBeam
        self.slabProp = slabProp
        self.fit_span_area = fitness_span_in_area
        self.fit_node_area = fitness_node_in_area
        self.repairMask = repairMask
        
        # Sınırların (Limits) Oluşturulması
        self.limits = {
            "col_size_max"         : len(xls["colSec"]["dL"]) - 1,
            "nod_ax_lens"          : np.array([len(ax) for ax in geoData["nodAx"]]),
            "col_ecc_choices"      : funcOpti.build_ecc_choices(xls["eccIntervals"]["col"]),
            "col_span_size_max"    : len(xls["colSpanSec"]["width"]) - 1,
            "col_span_ecc_choices" : funcOpti.build_ecc_choices(xls["eccIntervals"]["colSpan"]),
            "beam_size_max"        : len(xls["beamSec"]["h"]) - 1,
            "beam_ecc_choices"     : funcOpti.build_ecc_choices(xls["eccIntervals"]["beam"]),
            "slab_size_max"        : len(xls["slabSec"]["h"]) - 1
        }

        # En kötü durum fitness değerleri (Scaling için)
        self.worst_fitness_vals = funcOpti.find_worst_fitness(
            geoData, contBeam, fitness_span_in_area, fitness_node_in_area
        )

        # Popülasyon ve Tarihçe
        self.pop = []      # [raw_cand, processed_cand, fit_tuple, pen_tuple, obj_val]
        self.hPop = []     # Historical population (JAYA için)
        self.best_solution = None
        self.best_objective = np.inf
        self.best_penalty = None  # DÜZELTME: En iyi çözümün ceza değerlerini tutar
        self.history = []

    def _process_candidate_pipeline(self, raw_cand):
        """
        Tek bir ham çözüm adayını işleyerek değerlendirilebilir hale getiren işlem hattı.

        Bu metod, ham (raw) bir çözüm vektörünü alır ve sırasıyla şu işlemleri uygular:
        1. Yorumlama (Interpretation): Sürekli değerleri kesikli tasarım değişkenlerine çevirir.
        2. Onarım (Repair): Statik onarım maskelerini uygular.
        3. OD Onarımı (OD Repair): Dinamik onarım kurallarını (On-Demand) uygular.
        4. Değerlendirme: Ceza (Penalty) ve Uygunluk (Fitness) değerlerini hesaplar.

        Args:
            raw_cand (list): 0-1 aralığında değerlerden oluşan ham çözüm vektörü.

        Returns:
            tuple: (synced_raw, cand_final, fit_tuple, pen_tuple)
                - synced_raw: Onarımların yansıtıldığı ham vektör (Lamarckian için).
                - cand_final: İşlenmiş ve onarılmış nihai çözüm vektörü.
                - fit_tuple: Hesaplanmış fitness bileşenleri.
                - pen_tuple: Hesaplanmış ceza bileşenleri.
        """
        # F1. Yorumlama (Interpretation)
        cand_interp = funcOpti.interpret_solution(raw_cand, self.limits)

        # B & F3. Genel Maske Uygulama (Statik)
        cand_repaired = buildRepMask.apply_repair(cand_interp, self.repairMask)

        # A & F2. OD Maske Uygulama (Dinamik/On-Demand)
        od_mask = buildODRepair.build_data_od_repair(cand_repaired, self.geoData, self.contBeam)
        cand_final = buildODRepair.apply_od_repair(cand_repaired, od_mask)
        
        # Sync Raw (Lamarckian Learning) - DÜZELTME: Return değerine eklendi
        synced_raw = funcOpti.sync_raw_from_repaired(cand_final)

        # C & F4.1 Penalty Hesaplama
        pen_vals = buildPenalty.build_data_penalty(cand_final, self.geoData, self.xls)
        pen_tuple = np.array(pen_vals, dtype=float)

        # D & F4.2 Fitness Hesaplama
        fit_vals = buildFit.build_data_fitness(
            cand_final, self.geoData, self.contBeam, self.fit_span_area, self.fit_node_area
        )
        fit_tuple = np.array(fit_vals, dtype=float)

        return synced_raw, cand_final, fit_tuple, pen_tuple

    def _calculate_lemonge_objectives(self, population_subset):
        """
        Popülasyonun bir alt kümesi için Lemonge yöntemiyle amaç fonksiyonu değerlerini hesaplar.

        Lemonge yöntemi, popülasyon genelindeki ceza dağılımına göre dinamik ağırlıklar
        belirler. Bu nedenle hesaplama tekil adaylar yerine bir grup üzerinde yapılır.

        Args:
            population_subset (list): Değerlendirilecek aday çözümler listesi.
                                      Her öğe [raw, processed, fit, pen, obj] formatındadır.

        Returns:
            np.array: Her aday için hesaplanmış tekil amaç (objective) değerleri listesi.
        """
        if not population_subset: return []

        # Fitness tuple'larını matrise çevir
        all_fits = np.array([p[2] for p in population_subset])
        
        # Scalar Objective (Normalize edilmiş fitness)
        scalar_objs = funcOpti.compute_scalar_objective(all_fits, self.worst_fitness_vals)

        # Lemonge Parametreleri
        funcFact = [[None, None, None, None, [0, 1, 2, 3]], [None, np.ones(4)]]
        
        # Lemonge hesaplaması için geçici yapı
        temp_pop_structure = []
        for p in population_subset:
            # [raw(dummy), fitness(dummy), penalty_tuple, scalar_fitness(dummy)]
            temp_pop_structure.append([None, None, p[3], None])

        objectives = funcOpti.lemonge(temp_pop_structure, scalar_objs, funcFact)
        
        return objectives

    def run(self, pop_size=10, max_iter=20):
        """
        JAYA algoritması tabanlı optimizasyon döngüsünü çalıştırır.

        Belirtilen iterasyon sayısı boyunca popülasyonu evrimleştirir, her adımda
        yeni adaylar üretir ve Greedy Selection (Açgözlü Seçim) yöntemiyle
        bir sonraki nesli belirler.

        Args:
            pop_size (int): Popülasyon büyüklüğü (Aday çözüm sayısı).
            max_iter (int): Maksimum iterasyon sayısı.

        Returns:
            tuple: (best_solution, best_objective, history, initial_best_penalty, best_penalty)
                - best_solution (list): Bulunan en iyi çözüm vektörü.
                - best_objective (float): En iyi çözümün amaç fonksiyonu değeri.
                - history (list): Her iterasyondaki en iyi amaç değerlerinin listesi.
                - initial_best_penalty (np.array): İlk iterasyondaki en iyi çözümün ceza değerleri.
                - best_penalty (np.array): Final çözümün ceza değerleri.
        """
        print(f"\n--- Optimizasyon Başlatılıyor (Pop: {pop_size}, Iter: {max_iter}) ---")
        start_time = time.perf_counter()

        # A0. BAŞLANGIÇ POPÜLASYONU
        self.pop = []
        self.best_objective = np.inf
        self.best_solution = None
        self.best_penalty = None

        for _ in range(pop_size):
            raw_cand = funcOpti.gen_rand_sol(self.geoData, self.xls, len(self.contBeam))
            
            # İlk değerlendirme (Pipeline) - DÜZELTME: 4 değer dönüyor (synced_raw eklendi)
            synced_raw, processed_cand, fit_tuple, pen_tuple = self._process_candidate_pipeline(raw_cand)
            
            # [Raw, Processed, Fitness, Penalty, Objective(Placeholder)]
            self.pop.append([synced_raw, processed_cand, fit_tuple, pen_tuple, None])

        # İlk Lemonge Hesaplaması
        objs = self._calculate_lemonge_objectives(self.pop)
        for i in range(pop_size):
            self.pop[i][4] = objs[i]
            
            # En iyiyi kaydet
            if objs[i] < self.best_objective:
                self.best_objective = objs[i]
                self.best_solution = copy.deepcopy(self.pop[i][1])
                self.best_penalty = copy.deepcopy(self.pop[i][3]) # DÜZELTME: Penalty kaydı

        self.hPop = copy.deepcopy(self.pop) # JAYA Tarihçesi
        
        # DÜZELTME: İlk iterasyon penalty'sini sakla
        initial_best_penalty = copy.deepcopy(self.best_penalty)

        # DÖNGÜ BAŞLANGICI
        for iteration in range(max_iter):
            
            # F. YENİ ADAY ÜRETME (JAYA)
            new_raw_pop_structure, new_hPop_structure = funcOpti.ejaya(self.pop, self.hPop)

            # Yeni adayların geçici listesi
            offspring_pop = []

            # Güvenli candidate sayısı
            candidate_count = min(pop_size, len(new_raw_pop_structure))

            # Yeni adayları işle
            for i in range(candidate_count):
                new_raw = new_raw_pop_structure[i][0]
                synced_new_raw, proc_cand, fit, pen = self._process_candidate_pipeline(new_raw)
                offspring_pop.append([synced_new_raw, proc_cand, fit, pen, None])

            # F4.3 Yeni adaylar için Objective hesapla
            offspring_objs = self._calculate_lemonge_objectives(offspring_pop)

            # F5. KARŞILAŞTIRMA VE KABUL (Greedy Selection)
            for i in range(candidate_count):
                if i >= len(offspring_objs): continue

                offspring_pop[i][4] = offspring_objs[i]
                
                # Eğer yeni aday eskisinden iyiyse veya eşitse
                if offspring_objs[i] <= self.pop[i][4]:
                    # HAM halini ve işlenmiş verilerini kabul et
                    self.pop[i] = offspring_pop[i]
                
                # Global en iyiyi güncelle
                if self.pop[i][4] < self.best_objective:
                    self.best_objective = self.pop[i][4]
                    self.best_solution = copy.deepcopy(self.pop[i][1])
                    self.best_penalty = copy.deepcopy(self.pop[i][3]) # DÜZELTME: Penalty güncelleme
            
            # Tarihçeyi güncelle
            self.hPop = new_hPop_structure
            self.history.append(self.best_objective)
            print(f"Iter {iteration+1:02d} | Best Obj: {self.best_objective:.6f}")

        elapsed = time.perf_counter() - start_time
        print(f"--- Optimizasyon Tamamlandı ({elapsed:.2f}s) ---\n")
        
        # DÜZELTME: 5 değer döndürülüyor
        return self.best_solution, self.best_objective, self.history, initial_best_penalty, self.best_penalty