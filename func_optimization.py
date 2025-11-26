import numpy as np
import copy
import random

"""
Required by:
    build_ecc_choices
    generate_random_sol
    gen_rand_sol
    ejaya
    interpret_solution
    evaluate_solution
    find_worst_fitness
    normalize_fitness_values
    sync_raw_from_repaired
    _stochastic_round
"""

def build_ecc_choices(interval):
    """
    Belirtilen aralık değerine göre olası eksantriklik (kaçıklık) seçeneklerini oluşturur.

    Args:
        interval (int): Eksantriklik aralığı (bölüm sayısı).

    Returns:
        np.array: Olası eksantriklik değerlerini içeren dizi (örn: [-0.5, 0.0, 0.5]).
    """
    if interval == 0:
        return np.array([0.0])
    else:
        step = 0.5 / interval
        return np.arange(-0.5, 0.5 + step/2, step)

def generate_random_sol(nodes, colSec, nodAx, intCol, spans, colSpanSec, intColSpan,
                        beamSec, intBeam, contBeams, areas, slabSec):
    """
    Tüm yapı elemanları için rastgele değerlerden oluşan bir başlangıç çözüm vektörü üretir.

    Args:
        nodes (list): Düğüm noktaları listesi.
        colSec (list): Kolon kesit seçenekleri.
        nodAx (list): Düğümlerin bağlı olduğu aks bilgileri.
        intCol (int): Kolon eksantriklik aralığı.
        spans (list): Açıklık (kiriş hattı) listesi.
        colSpanSec (list): Perde (çizgisel kolon) kesit seçenekleri.
        intColSpan (int): Perde eksantriklik aralığı.
        beamSec (list): Kiriş kesit seçenekleri.
        intBeam (int): Kiriş eksantriklik aralığı.
        contBeams (list): Sürekli kiriş hatları.
        areas (list): Döşeme alanları.
        slabSec (list): Döşeme kalınlık seçenekleri.

    Returns:
        list: Rastgele oluşturulmuş tasarım değişkenlerini içeren liste.
    """
    # 1. Noktasal Kolon
    colTopo   = np.random.randint(0, 2, size=len(nodes))
    colSize   = np.random.randint(0, len(colSec), size=len(nodes))
    len_nodAx = [len(i) for i in nodAx]
    colDirec  = np.random.randint(0, max(len_nodAx), size=len(nodes))
    colDirec  = np.mod(colDirec, len_nodAx)
    colEccChoices = build_ecc_choices(intCol)
    colEccL       = np.random.choice(colEccChoices, size=len(nodes))
    colEccS       = np.random.choice(colEccChoices, size=len(nodes))

    # 2. Çizgisel Kolon
    colSpanTopo = np.random.randint(0, 2, size=len(spans))
    colSpanSize = np.random.randint(0, len(colSpanSec), size=len(spans))
    colSpanEcc  = np.random.choice(build_ecc_choices(intColSpan), size=len(spans))

    # 3. Kiriş
    beamTopo = np.random.randint(0, 2, size=len(spans))
    beamSize = np.random.randint(0, len(beamSec), size=len(spans))
    beamEcc  = np.random.choice(build_ecc_choices(intBeam), size=len(spans))

    # 4. Sürekli Kiriş
    contBeamTopo = np.random.randint(-1, 2, size=len(contBeams))

    # 5. Döşeme
    slabSize = np.random.randint(0, len(slabSec), size=len(areas))

    return [
        colTopo, colSize, colDirec, colEccL, colEccS,
        colSpanTopo, colSpanSize, colSpanEcc,
        beamTopo, beamSize, beamEcc,
        contBeamTopo, slabSize
    ]

def gen_rand_sol(geoData, xls, contBeamLen):
    """
    generate_random_sol fonksiyonunu proje veri yapılarını kullanarak çağıran yardımcı fonksiyon.

    Args:
        geoData (dict): Geometrik veriler.
        xls (dict): Excel'den okunan kısıt ve kesit verileri.
        contBeamLen (int): Sürekli kiriş sayısı.

    Returns:
        list: Rastgele çözüm vektörü.
    """
    return generate_random_sol(
        nodes      = geoData["nodes"],
        colSec     = xls["colSec"]["dL"],
        nodAx      = geoData["nodAx"],
        intCol     = xls["eccIntervals"]["col"],
        spans      = geoData["spans"],
        colSpanSec = xls["colSpanSec"]["width"],
        intColSpan = xls["eccIntervals"]["colSpan"],
        beamSec    = xls["beamSec"]["h"],
        intBeam    = xls["eccIntervals"]["beam"],
        contBeams  = np.empty(contBeamLen),
        areas      = geoData["areas"],
        slabSec    = xls["slabSec"]["h"]
    )

# -------------------------------------------------
# --------------- GENERAL OPERATORS ---------------
# -------------------------------------------------

def addVecs(vec1, vec2):
    """İki vektörü eleman bazlı toplar."""
    return [v1+v2 for v1,v2 in zip(vec1,vec2)]

def subVecs(vec1, vec2):
    """Birinci vektörden ikinci vektörü eleman bazlı çıkarır."""
    return [v1-v2 for v1,v2 in zip(vec1,vec2)]

def scaVec(scalar, vec):
    """Bir vektörü skaler bir sayı ile çarpar."""
    return [scalar*v for v in vec]

def mulVecs(vec1, vec2):
    """İki vektörü eleman bazlı çarpar."""
    return [v1*v2 for v1,v2 in zip(vec1,vec2)]

def bestWorst(pop):
    """
    Popülasyon içindeki en iyi (minimum fitness) ve en kötü (maksimum fitness) çözümleri bulur.

    Args:
        pop (list): Popülasyon listesi.

    Returns:
        tuple: (bestSol, worstSol)
    """
    fitVals  = np.array([sol[-1] for sol in pop])
    bestSol  = pop[np.argmin(fitVals)]
    worstSol = pop[np.argmax(fitVals)]
    return bestSol, worstSol

def findMean(pop):
    """
    Popülasyonun ortalama çözüm vektörünü hesaplar.

    Args:
        pop (list): Popülasyon listesi.

    Returns:
        list: Ortalama değerlerden oluşan çözüm vektörü.
    """
    meanSol, popVec = [], [sol[0] for sol in pop]
    for i in range(len(popVec[0])):
        meanSol.append(np.mean([vec[i] for vec in popVec], axis=0))
    meanSol.extend([np.nan, np.nan, np.nan])
    return meanSol

def randVecs(cand):
    """
    Verilen aday çözümün boyutlarına uygun rastgele (0-1 arası) vektörler üretir.

    Args:
        cand (list): Referans aday çözüm.

    Returns:
        list: Rastgele sayılardan oluşan vektörler listesi.
    """
    return [np.random.rand(len(vec)) for vec in cand[0]]

# --------------------------------------------------
# ----------------- METAHEURISTICS -----------------
# --------------------------------------------------

def ejaya(pop, hPop):
    """
    Geliştirilmiş JAYA (e-JAYA) algoritması hareket operatörü.
    
    Mevcut popülasyon ve tarihçe popülasyonunu kullanarak yeni aday çözümler üretir.
    En iyi çözüme yaklaşmaya ve en kötü çözümden uzaklaşmaya çalışır.

    Args:
        pop (list): Mevcut popülasyon.
        hPop (list): Tarihçe (önceki iterasyon) popülasyonu.

    Returns:
        tuple: (candPop, histPop) -> Yeni aday popülasyonu ve güncellenmiş tarihçe.
    """
    if np.random.rand() > 0.5 : histPop = copy.deepcopy(hPop)
    else                      : histPop = copy.deepcopy(pop)
    random.shuffle(histPop)

    bestSol, worstSol = bestWorst(pop) 
    
    r3, r4  = np.random.rand(), np.random.rand()
    meanSol = findMean(pop)
    Pu      = addVecs ( scaVec(r3, bestSol[0]),  scaVec(1-r3, meanSol[0]) )
    Pl      = addVecs ( scaVec(r4, worstSol[0]), scaVec(1-r4, meanSol[0]) )

    candPop = []
    
    for i,sol in enumerate(pop):
        if np.random.rand() > 0.5:
            r5, r6 = randVecs(sol), randVecs(sol)
            ex1    = mulVecs(r5, subVecs(Pu, sol[0]))
            ex2    = mulVecs(r6, subVecs(Pl, sol[0]))
            cand   = subVecs( addVecs(sol[0], ex1), ex2 )
        else:
            k    = np.random.randn()
            ex1  = subVecs(histPop[i][0], sol[0])
            cand = addVecs(sol[0], scaVec(k, ex1))
        
        candPop.append([cand, np.nan, np.nan, np.nan])
    
    return candPop, histPop

# --------------------------------------------------
# -------------- CONSTRAINT HANDLING ---------------
# --------------------------------------------------

def lemonge_K(pop, scalObj, funcFact):
    """
    Lemonge yöntemi için dinamik ceza ağırlıklarını (K katsayıları) hesaplar.

    Popülasyondaki ortalama ihlal değerlerine göre, sık ihlal edilen kısıtların
    ağırlığını artırarak algoritmayı o yönde baskılar.

    Args:
        pop (list): Popülasyon verisi.
        scalObj (np.array): Ölçeklenmiş amaç fonksiyon değerleri.
        funcFact (list): Ceza indeksi parametrelerini içeren yapı.

    Returns:
        np.array: Her bir ceza türü için hesaplanan ağırlık katsayıları (Kj).
    """
    abs_fmean = np.abs(np.mean(scalObj))
    penalty_vectors = np.array([sol[-2] for sol in pop], dtype=float)
    
    vAvg = np.mean(penalty_vectors, axis=0)
    vAvgSqr = np.sum(vAvg ** 2)
    
    if vAvgSqr == 0:
        return np.ones_like(vAvg)
    
    # funcFact[0][4] -> Penalty Index List
    penIdx = funcFact[0][4]
    
    kj = np.zeros_like(vAvg)
    for j in penIdx:
        kj[j] = (abs_fmean / vAvgSqr) * vAvg[j]
    return kj

def lemonge_F(pop, scalObj, REFscalObj=None):
    """
    Lemonge yöntemi için düzeltilmiş amaç fonksiyon değerlerini (F) hesaplar.
    
    Cezası olan çözümlerin amaç fonksiyon değerini, popülasyon ortalamasına
    göre ayarlayarak 'fBar' değerini oluşturur.

    Args:
        pop (list): Popülasyon.
        scalObj (np.array): Ölçeklenmiş ham fitness değerleri.
        REFscalObj (np.array, optional): Referans fitness değerleri.

    Returns:
        np.array: Düzeltilmiş fitness değerleri listesi.
    """
    if REFscalObj is None: fMean = np.mean(scalObj)
    else: fMean = np.mean(REFscalObj)
    
    fBar = np.array([f if f > fMean else fMean for f in scalObj], dtype=float)
    fList = []
    
    for i in range(len(pop)):
        penalty_sum = np.sum(pop[i][-2])
        if penalty_sum == 0: fList.append(scalObj[i])
        else: fList.append(fBar[i])
    return np.array(fList)

def lemonge(pop, scalObj, funcFact, REFpop=None, REFscalObj=None):
    """
    Adaptif ceza yöntemi (Lemonge) ile nihai amaç fonksiyon değerini hesaplar.

    Fitness ve ceza değerlerini dinamik ağırlıklarla birleştirerek tek bir
    skor (Objective Value) üretir.

    Args:
        pop (list): Popülasyon.
        scalObj (np.array): Ölçeklenmiş fitness değerleri.
        funcFact (list): Ceza parametreleri.
        REFpop (list, optional): Referans popülasyon.
        REFscalObj (np.array, optional): Referans fitness değerleri.

    Returns:
        np.array: Her birey için hesaplanmış nihai skorlar.
    """
    if REFpop is None: Kpop = pop
    else: Kpop = REFpop
    
    if REFscalObj is None: Kscal = scalObj
    else: Kscal = REFscalObj
    
    kj = lemonge_K(Kpop, Kscal, funcFact)
    fList = lemonge_F(pop, scalObj, REFscalObj)
    
    fitness = []
    for i in range(len(pop)):
        penalty_vector = np.array(pop[i][-2], dtype=float)
        penalty_term = np.sum(kj * penalty_vector)
        fitness.append(fList[i] + penalty_term)
    return np.array(fitness)

def compute_scalar_objective(fitness_tuples, worst_fitness_values):
    """
    Çok amaçlı fitness değerlerini, en kötü duruma göre ölçekleyerek tekil (skaler) bir değere indirger.

    Args:
        fitness_tuples (np.array): Bireylerin fitness vektörleri.
        worst_fitness_values (np.array): Teorik en kötü fitness değerleri.

    Returns:
        np.array: Normalize edilmiş skaler fitness değerleri.
    """
    worst_safe = np.where(worst_fitness_values == 0.0, 1.0, worst_fitness_values)
    scaled = fitness_tuples / worst_safe
    return np.mean(scaled, axis=1)

# --------------------------------------------------
# ------------- SOLUTION INTERPRETATION ------------
# --------------------------------------------------

def _stochastic_round(raw_vec):
    """
    Vektörü stokastik (olasılıksal) olarak tamsayıya yuvarlar.
    Örn: 3.7 -> %70 ihtimalle 4, %30 ihtimalle 3.

    Args:
        raw_vec (np.array): Float değerlerden oluşan vektör.

    Returns:
        np.array: Tamsayıya yuvarlanmış vektör.
    """
    floor_val = np.floor(raw_vec)
    prob = raw_vec - floor_val
    mask = np.random.rand(len(raw_vec)) < prob
    return floor_val.astype(int) + mask.astype(int)

def _interpret_topology(raw_vec, min_val, max_val):
    """Topoloji (var/yok) değişkenlerini yorumlar."""
    rounded = _stochastic_round(raw_vec)
    clamped = np.clip(rounded, min_val, max_val)
    return clamped

def _interpret_size(raw_vec, max_idx):
    """Boyut/Kesit indeksi değişkenlerini yorumlar."""
    rounded = _stochastic_round(raw_vec)
    clamped = np.clip(rounded, 0, max_idx)
    return clamped

def _interpret_direction(raw_vec, nod_ax_lens):
    """Kolon yönü değişkenlerini aks sayısına göre yorumlar."""
    rounded = _stochastic_round(raw_vec)
    clamped = np.maximum(0, rounded)
    interpreted = clamped % nod_ax_lens
    return interpreted

def _interpret_eccentricity(raw_vec, choices):
    """
    Eksantriklik değerlerini en yakın geçerli seçeneğe yuvarlar.
    
    Args:
        raw_vec (np.array): Ham float değerler.
        choices (np.array): Geçerli eksantriklik seçenekleri.

    Returns:
        np.array: Seçenekler havuzundan seçilmiş değerler.
    """
    diffs = np.abs(raw_vec[:, np.newaxis] - choices[np.newaxis, :])
    nearest_indices = np.argmin(diffs, axis=1)
    interpreted = choices[nearest_indices]
    return interpreted

def interpret_solution(raw_cand, limits):
    """
    Sürekli (float) uzaydaki optimizasyon değişkenlerini, ayrık (discrete) tasarım değişkenlerine dönüştürür.
    
    Bu işlem, optimizasyonun sayısal uzayda çalışıp, sonucun inşaat parametrelerine
    dönüştürülmesini sağlar.

    Args:
        raw_cand (list): Ham aday çözüm vektörü.
        limits (dict): Değişkenlerin alabileceği maksimum ve minimum sınırlar.

    Returns:
        list: Yorumlanmış (tamsayı ve seçimlere dönüştürülmüş) çözüm vektörü.
    """
    interpreted_cand = copy.deepcopy(raw_cand)
    
    interpreted_cand[0] = _interpret_topology(raw_cand[0], 0, 1)
    interpreted_cand[1] = _interpret_size(raw_cand[1], limits["col_size_max"])
    interpreted_cand[2] = _interpret_direction(raw_cand[2], limits["nod_ax_lens"])
    interpreted_cand[3] = _interpret_eccentricity(raw_cand[3], limits["col_ecc_choices"])
    interpreted_cand[4] = _interpret_eccentricity(raw_cand[4], limits["col_ecc_choices"])
    interpreted_cand[5] = _interpret_topology(raw_cand[5], 0, 1)
    interpreted_cand[6] = _interpret_size(raw_cand[6], limits["col_span_size_max"])
    interpreted_cand[7] = _interpret_eccentricity(raw_cand[7], limits["col_span_ecc_choices"])
    interpreted_cand[8] = _interpret_topology(raw_cand[8], 0, 1)
    interpreted_cand[9] = _interpret_size(raw_cand[9], limits["beam_size_max"])
    interpreted_cand[10] = _interpret_eccentricity(raw_cand[10], limits["beam_ecc_choices"])
    interpreted_cand[11] = _interpret_topology(raw_cand[11], -1, 1)
    interpreted_cand[12] = _interpret_size(raw_cand[12], limits["slab_size_max"])

    return interpreted_cand

def evaluate_solution(raw_cand, limits, fitness_func):
    """
    Bir aday çözümü yorumlar ve fitness değerini hesaplar.

    Args:
        raw_cand (list): Ham aday çözüm.
        limits (dict): Sınır değerleri.
        fitness_func (callable): Fitness hesaplama fonksiyonu.

    Returns:
        float/tuple: Hesaplanan fitness değeri.
    """
    interpreted_cand = interpret_solution(copy.deepcopy(raw_cand), limits)
    fitness_val = fitness_func(interpreted_cand)
    return fitness_val

def sync_raw_from_repaired(repaired_cand):
    """
    Onarılmış (repaired) tasarım değişkenlerini tekrar float formatına senkronize eder.
    
    Lamarckian Learning prensibi gereği, onarım aşamasında yapılan iyileştirmelerin
    genetik koda (ham vektöre) geri yazılmasını sağlar.

    Args:
        repaired_cand (list): Onarılmış ve geçerli hale getirilmiş çözüm.

    Returns:
        list: Float tipine dönüştürülmüş ham vektör.
    """
    synced_raw = []
    for vec in repaired_cand:
        synced_raw.append(vec.astype(float))
    return synced_raw

def find_worst_fitness(geoData, contBeam, fitness_span_in_area, fitness_node_in_area):
    """
    Normalizasyon işlemi için teorik olarak mümkün olan en kötü fitness değerlerini hesaplar.
    
    Bu değerler, farklı ölçekteki fitness hedeflerini (örn: alan maliyeti vs kiriş sayısı)
    birbirine göre normalize etmek için kullanılır.

    Args:
        geoData (dict): Geometrik veriler.
        contBeam (list): Sürekli kiriş verisi.
        fitness_span_in_area (np.array): Alan maliyeti matrisi.
        fitness_node_in_area (np.array): Düğüm maliyeti vektörü.

    Returns:
        np.array: En kötü durum fitness değerlerini içeren vektör.
    """
    import numpy as np
    from build_data_fitness import (
        build_fitness_crossing_beams,
        build_fitness_standalone_beams,
    )
    spans_len = len(geoData["spans"])
    nodes_len = len(geoData["nodes"])
    spanLen   = geoData["spanLen"]
    spans     = geoData["spans"]
    nodSpan   = geoData["nodSpan"]
    spanAx    = geoData["spanAx"]

    full_beamTopo     = np.ones(spans_len, dtype=int)
    full_colTopo      = np.ones(nodes_len, dtype=int)
    full_colSpanTopo  = np.ones(spans_len, dtype=int)
    null_contBeamTopo = np.zeros(len(contBeam), dtype=int)

    worst_span_in_area = np.sum((full_colSpanTopo + full_beamTopo) * fitness_span_in_area)
    worst_node_in_area = np.sum(full_colTopo * fitness_node_in_area)
    worst_standalone_beams = build_fitness_standalone_beams(
        full_beamTopo, null_contBeamTopo, contBeam, spanLen,
    )
    zero_colTopo     = np.zeros(nodes_len, dtype=int)
    zero_colSpanTopo = np.zeros(spans_len, dtype=int)
    worst_crossing_beams = build_fitness_crossing_beams(
        zero_colTopo, zero_colSpanTopo, full_beamTopo, spans, nodSpan, spanAx, spanLen,
    )

    return np.array(
        [worst_span_in_area, worst_node_in_area, worst_standalone_beams, worst_crossing_beams],
        dtype=float,
    )

def normalize_fitness_values(pop_fitness_tuples, worst_fitness_values):
    """
    Ham fitness değerlerini 0 ile 1 arasına normalize eder.

    Args:
        pop_fitness_tuples (np.array): Popülasyonun fitness değerleri.
        worst_fitness_values (np.array): En kötü durum referans değerleri.

    Returns:
        np.array: 0-1 arasına sıkıştırılmış normalize fitness değerleri.
    """
    worst_safe = np.where(worst_fitness_values == 0.0, 1.0, worst_fitness_values)
    norm = pop_fitness_tuples / worst_safe
    return np.clip(norm, 0.0, 1.0)