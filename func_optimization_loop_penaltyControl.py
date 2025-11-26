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
            tuple: (cand_final, fit_tuple, pen_tuple)
                - cand_final (list): İşlenmiş ve onarılmış nihai çözüm vektörü.
                - fit_tuple (np.array): Hesaplanmış fitness bileşenleri.
                - pen_tuple (np.array): Hesaplanmış ceza bileşenleri.
        """
        # F1. Yorumlama (Interpretation)
        cand_interp = funcOpti.interpret_solution(raw_cand, self.limits)

        # B & F3. Genel Maske Uygulama (Statik)
        cand_repaired = buildRepMask.apply_repair(cand_interp, self.repairMask)

        # A & F2. OD Maske Uygulama (Dinamik/On-Demand)
        od_mask = buildODRepair.build_data_od_repair(cand_repaired, self.geoData, self.contBeam)
        cand_final = buildODRepair.apply_od_repair(cand_repaired, od_mask)

        # C & F4.1 Penalty Hesaplama
        pen_vals = buildPenalty.build_data_penalty(cand_final, self.geoData, self.xls)
        pen_tuple = np.array(pen_vals, dtype=float)

        # D & F4.2 Fitness Hesaplama
        fit_vals = buildFit.build_data_fitness(
            cand_final, self.geoData, self.contBeam, self.fit_span_area, self.fit_node_area
        )
        fit_tuple = np.array(fit_vals, dtype=float)

        return cand_final, fit_tuple, pen_tuple

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

    def run(self, pop_size, max_iter):
        """
        JAYA algoritması tabanlı optimizasyon döngüsünü çalıştırır.

        Belirtilen iterasyon sayısı boyunca popülasyonu evrimleştirir, her adımda
        yeni adaylar üretir ve Greedy Selection (Açgözlü Seçim) yöntemiyle
        bir sonraki nesli belirler.

        Args:
            pop_size (int): Popülasyon büyüklüğü (Aday çözüm sayısı).
            max_iter (int): Maksimum iterasyon sayısı.

        Returns:
            tuple: (best_solution, best_objective, history)
                - best_solution (list): Bulunan en iyi çözüm vektörü.
                - best_objective (float): En iyi çözümün amaç fonksiyonu değeri.
                - history (list): Her iterasyondaki en iyi amaç değerlerinin listesi.
        """
        print(f"\n--- Optimizasyon Başlatılıyor (Pop: {pop_size}, Iter: {max_iter}) ---")
        start_time = time.perf_counter()

        # A0. BAŞLANGIÇ POPÜLASYONU
        self.pop = []
        for _ in range(pop_size):
            raw_cand = funcOpti.gen_rand_sol(self.geoData, self.xls, len(self.contBeam))
            
            # İlk değerlendirme (Pipeline)
            processed_cand, fit_tuple, pen_tuple = self._process_candidate_pipeline(raw_cand)
            
            # [Raw, Processed, Fitness, Penalty, Objective(Placeholder)]
            self.pop.append([raw_cand, processed_cand, fit_tuple, pen_tuple, None])

        # İlk Lemonge Hesaplaması
        objs = self._calculate_lemonge_objectives(self.pop)
        for i in range(pop_size):
            self.pop[i][4] = objs[i]
            
            # En iyiyi kaydet
            if objs[i] < self.best_objective:
                self.best_objective = objs[i]
                self.best_solution = copy.deepcopy(self.pop[i][1]) # Processed halini sakla

        self.hPop = copy.deepcopy(self.pop) # JAYA Tarihçesi

        # DÖNGÜ BAŞLANGICI
        for iteration in range(max_iter):
            
            # F. YENİ ADAY ÜRETME (JAYA)
            new_raw_pop_structure, new_hPop_structure = funcOpti.ejaya(self.pop, self.hPop)

            # DEBUG: ejaya dönüşünü kontrol et
            print(f"[DEBUG] iteration {iteration+1}: len(new_raw_pop_structure) = {len(new_raw_pop_structure)}, expected pop_size = {pop_size}")
            if len(new_raw_pop_structure) < pop_size:
                print(f"[DEBUG] ejaya returned fewer candidates ({len(new_raw_pop_structure)}) than pop_size ({pop_size}). Using min value.")

            # Yeni adayların geçici listesi
            offspring_pop = []

            # Güvenli candidate sayısı (ejaya'nın döndürdüğü kadar veya pop_size kadar)
            candidate_count = min(pop_size, len(new_raw_pop_structure))
            if candidate_count == 0:
                # Eğer hiç aday üretilmediyse iterasyonu atla (logla)
                print(f"[WARNING] iteration {iteration+1}: ejaya ürettiği aday sayısı 0. İterasyon atlanıyor.")
                # hPop'u yine de güncelle (ejaya döndürdüğünü kullan)
                self.hPop = new_hPop_structure
                # Tarihçe ve log
                self.history.append(self.best_objective)
                print(f"Iter {iteration+1:02d} | Best Obj: {self.best_objective:.6f}")
                continue

            # Yeni adayları işle (F1, F2, F3, F4)
            for i in range(candidate_count):
                try:
                    new_raw = new_raw_pop_structure[i][0]
                except Exception as e:
                    print(f"[ERROR] iteration {iteration+1}: new_raw_pop_structure[{i}] erişim hatası: {e}")
                    continue

                proc_cand, fit, pen = self._process_candidate_pipeline(new_raw)
                offspring_pop.append([new_raw, proc_cand, fit, pen, None])

            # DEBUG: offspring_pop kısa özet ve penalty kontrolü
            print(f"[DEBUG] iteration {iteration+1}: offspring_pop size = {len(offspring_pop)}")
            if offspring_pop:
                # Penalty'leri float matris olarak almaya çalış
                try:
                    penalties = np.array([p[3] for p in offspring_pop], dtype=float)
                except Exception:
                    # Eğer dtype=float dönüşümü başarısız olursa object array dönüyor; o zaman ayrı yol
                    penalties = np.array([p[3] for p in offspring_pop], dtype=object)

                # Güvenli istatistik basımı
                if penalties.size == 0:
                    print("[DEBUG] offspring penalties empty")
                else:
                    # Eğer penalties object array ise sütun bilgisi garanti değil; güvenli erişim
                    if penalties.dtype == object:
                        print("[DEBUG] offspring penalties (object dtype), showing first 3 entries:")
                        for p in penalties[:3]:
                            print("  ", p)
                    else:
                        # numeric matris ise mean/std/unique güvenli
                        try:
                            print("offspring penalties mean/std/unique:",
                                  penalties.mean(axis=0), penalties.std(axis=0))
                            unique_pen = np.unique(penalties, axis=0)
                            print("unique penalty vectors (first 10):", unique_pen[:10])
                        except Exception as e:
                            print(f"[DEBUG] penalty istatistik hesaplanamadı: {e}")
            else:
                print("[DEBUG] offspring_pop boş, penalty istatistikleri atlandı.")

            # F4.3 Yeni adaylar için Objective hesapla
            offspring_objs = self._calculate_lemonge_objectives(offspring_pop)

            # F5. KARŞILAŞTIRMA VE KABUL (Greedy Selection)
            # Sadece candidate_count kadar karşılaştırma yap (ejaya daha az döndü ise)
            for i in range(candidate_count):
                # Güvenlik: eğer offspring_objs kısa ise atla
                if i >= len(offspring_objs):
                    print(f"[WARNING] offspring_objs eksik: i={i}, len={len(offspring_objs)}. Atlanıyor.")
                    continue

                offspring_pop[i][4] = offspring_objs[i]
                
                # Eğer yeni aday eskisinden iyiyse veya eşitse
                if offspring_objs[i] <= self.pop[i][4]:
                    # HAM halini ve işlenmiş verilerini kabul et
                    self.pop[i] = offspring_pop[i]
                
                # Global en iyiyi güncelle
                if self.pop[i][4] < self.best_objective:
                    self.best_objective = self.pop[i][4]
                    self.best_solution = copy.deepcopy(self.pop[i][1])
            
            # Tarihçeyi güncelle
            self.hPop = new_hPop_structure
            self.history.append(self.best_objective)
            print(f"Iter {iteration+1:02d} | Best Obj: {self.best_objective:.6f}")

        elapsed = time.perf_counter() - start_time
        print(f"--- Optimizasyon Tamamlandı ({elapsed:.2f}s) ---\n")
        
        return self.best_solution, self.best_objective, self.history