import numpy as np
"""
Required by:
    build_penalty_beam_lengths
    build_penalty_beam_dist
    build_penalty_col_dist
    build_penalty_beam_with_free_end
"""





def build_penalty_beam_lengths(
    colTopo, colSpanTopo, beamTopo, axNod, nodeDist, axSpan, beamLenLimMin, beamLenLimMax):
    """
    ONDEMAND : Kolon bulunmayan düğümlere saplanan kirişlerin toplam uzunluğunu hesaplar.
    Kirişler tüm sağlandığı düğümlerde değerlendirilir.

    Args:
        colTopo (np.ndarray)      : Sistemde bulunan noktasal kolonların topolojisi
        colSpanTopo (np.ndarray)  : Sistemde bulunan çizgisel kolonların topolojisi
        beamTopo (np.ndarray)     : Sistemde bulunan kirişların topolojisi
        axNod (list)              : Her bir aksın üzerinde bulunan düğümlerin indekslerini
                                    içeren liste
        nodeDist (np.ndarray)     : Her bir düğüm çiftinin arasındaki mesafeyi içeren 2B dizi
        axSpan (list)             : Her bir aksın üzerinde bulunan aks parçalarının indekslerini
                                    içeren liste
        beamLenLimMin (float)     : Kiriş uzunluğu alt sınırı
        beamLenLimMax (float)     : Kiriş uzunluğu üst sınırı

    Returns:
        Sistemde bulunan ve uzunluk sınırlarını ihlal eden kirişlerin ihlal oranları toplamı

    Requires:
        numpy
    """
    beam_lengths = []

    for i in range(len(axSpan)):
        nodes, spans     = axNod[i], axSpan[i] # aks üzerindeki düğüm ve span indeksleri
        current_beam_len = 0 # kiriş uzunluğu başlangıç değeri

        for j, span in enumerate(spans):

            has_colspan = colSpanTopo[span] == 1 # aks parçasında çizgisel kolon var mı?
            has_beam    = beamTopo[span] == 1 # aks parçasında kiriş var mı?

            # eğer aks parçasında çizgisel kolon varsa kiriş sonuna geldik demektir.
            if has_colspan:

                if current_beam_len > 0:
                    beam_lengths.append(current_beam_len)
                    current_beam_len = 0
            
            # eğer aks parçasında kiriş varsa kiriş uzunluğunu güncelle
            elif has_beam:
                n1, n2 = nodes[j], nodes[j+1]
                current_beam_len += nodeDist[n1, n2]
                # kirişin bitiş düğümünde kolon varsa kiriş sonuna geldik demektir.
                if colTopo[n2] == 1:
                    beam_lengths.append(current_beam_len)
                    current_beam_len = 0

            # eğer aks parçasında ne çizgisel kolon ne de kiriş varsa kiriş sonuna geldik
            # demektir.
            else:

                if current_beam_len > 0:
                    beam_lengths.append(current_beam_len)
                    current_beam_len = 0

        # aks sonunda kiriş kalmışsa bu kirişin de uzunluğunu listeye ekle
        if current_beam_len > 0:
            beam_lengths.append(current_beam_len)

    # Toplam cezanın hesaplanması
    beam_lengths = np.array(beam_lengths)
    
    mask_low  = beam_lengths < beamLenLimMin
    mask_high = beam_lengths > beamLenLimMax

    penalty  = np.sum((beamLenLimMin / beam_lengths[mask_low]) - 1)
    penalty += np.sum((beam_lengths[mask_high] / beamLenLimMax) - 1)

    # Toplam cezayı döndür
    return penalty





def build_penalty_beam_dist(beamTopo, spanDistMin, spanDistMax, beamDistMin, beamDistMax):
    """
    Kirişler arasında izin verilen minimum ve maksimum mesafe sınırlarının ihlal derecesini
    hesaplar.

    Args:
        beamTopo (np.ndarray)    : Sistemde bulunan kirişlerin topolojisi (1=var, 0=yok)
        spanDistMin (np.ndarray) : Kiriş çiftlerinin arasındaki minimum mesafeyi içeren 2B dizi
        spanDistMax (np.ndarray) : Kiriş çiftlerinin arasındaki maksimum mesafeyi içeren 2B dizi
        beamDistMin (float)      : Kirişler arası minimum mesafe sınırı
        beamDistMax (float)      : Kirişler arası maksimum mesafe sınırı
    
    Returns:
        Sistemde bulunan ve mesafe sınırlarını ihlal eden kiriş çiftlerinin ihlal oranları toplamı
    
    Requires:
        numpy as np
    """
    # 1. Aktif kirişleri seç
    active_idx = np.where(beamTopo == 1)[0]

    # 2. Kiriş çiftleri arasındaki en büyük ve en küçük mesafeleri
    # ayrı numpy dizilerine al
    spanMin = spanDistMin[np.ix_(active_idx, active_idx)].copy()
    spanMax = spanDistMax[np.ix_(active_idx, active_idx)].copy()

    # 3. Aralarında bir mesafeden söz edilemeyen kiriş çiftleri için -1 değeri döner.
    #    Bu değerleri ortalama ile değiştirerek etkisiz hale getir.
    neutral = (beamDistMin + beamDistMax) / 2
    spanMin[spanMin == -1] = neutral
    spanMax[spanMax == -1] = neutral

    # 4. Küçük ve büyük mesafeler için cezalar
    penalty_low  = np.where(spanMin < beamDistMin, (beamDistMin / spanMin) - 1, 0)
    penalty_high = np.where(spanMax > beamDistMax, (spanMax / beamDistMax) - 1, 0)

    # 5. Üst üçgen (i<j) elemanları dikkate al → çift sayımı önlemek için
    triu_mask = np.triu(np.ones_like(spanMin, dtype=bool), k=1)

    # 6. Toplam cezayı hesapla ve döndür
    penalty = penalty_low[triu_mask].sum() + penalty_high[triu_mask].sum()

    return penalty





def build_penalty_col_dist(colTopo, colSpanTopo, nodeDist, spans, colDistMin, colDistMax):
    """
    Noktasal ve çizgisel kolonlar arasında izin verilen minimum ve maksimum mesafe sınırlarının
    ihlal derecesini hesaplar.

    Args:
        colTopo (np.ndarray)     : Sistemde bulunan noktasal kolonların topolojisi (1=var, 0=yok)
        colSpanTopo (np.ndarray) : Sistemde bulunan çizgisel kolonların topolojisi (1=var, 0=yok)
        nodeDist (np.ndarray)    : Düğüm çiftleri arasındaki mesafeleri içeren 2B dizi
        spans (np.ndarray)       : Aks parçalarının uç düğümlerini içeren dizi
        colDistMin (float)       : Kolonlar arası minimum mesafe sınırı
        colDistMax (float)       : Kolonlar arası maksimum mesafe sınırı

    Returns:
        Sistemde bulunan ve mesafe sınırlarını ihlal eden noktasal ve çizgisel kolonların ihlal
        oranları toplamı

    Requires:
        numpy as np
    """
    # 1. Noktasal ve çizgisel kolon düğümlerini bul
    col_nodes     = np.where(colTopo == 1)[0]
    colSpan_nodes = spans[colSpanTopo == 1].ravel()
    col_nodes     = np.unique(np.concatenate([col_nodes, colSpan_nodes]))

    if len(col_nodes) < 2: return 0  # Tek kolon varsa ceza yok

    # 2. Sistemde bulunan kolon düğümlerine ait çiftlerin mesafe matrisini oluştur
    distMat = nodeDist[np.ix_(col_nodes, col_nodes)].copy()

    # 3. Matriste eğer iki düğüm aynı ise 0, iki düğüm arasında bir mesafeden söz
    #    edilemiyorsa -1 değeri vardır. Bu değerleri ortalama ile değiştirerek etkisiz
    #    hale getir.
    neutral = (colDistMin + colDistMax) / 2
    distMat[distMat <= 0] = neutral

    # 4. Küçük ve büyük mesafeler için cezalar
    penalty_low  = np.where(distMat < colDistMin, (colDistMin / distMat) - 1, 0)
    penalty_high = np.where(distMat > colDistMax, (distMat / colDistMax) - 1, 0)

    # 5. Üst üçgen (i<j) elemanları dikkate al → çift sayımı önlemek için
    triu_mask = np.triu(np.ones_like(distMat, dtype=bool), k=1)

    # 6. Toplam cezayı hesapla ve döndür
    penalty = penalty_low[triu_mask].sum() + penalty_high[triu_mask].sum()

    return penalty





def build_penalty_beam_with_free_end(colTopo, colSpanTopo, beamTopo, spans, spanLen):
    """
    Her iki ucu da tutulu olmayan kirişlerin toplam uzunluğunu döndürür.
    Tutulu uç:
        - Noktasal kolon varsa
        - Çizgisel kolon bağlıysa
        - Başka bir kirişin ucu varsa

    Args:
        colTopo (np.ndarray)     : Noktasal kolon varlık bilgisi (1=var, 0=yok)
        colSpanTopo (np.ndarray) : Çizgisel kolon varlık bilgisi (1=var, 0=yok)
        beamTopo (np.ndarray)    : Kiriş varlık bilgisi (1=var, 0=yok)
        spans (np.ndarray)       : Aks parçalarının başlangıç ve bitiş düğüm indeksleri
        spanLen (np.ndarray)     : Her bir aks parçasının uzunluğu

    Returns:
        En az bir ucu serbest olan kirişlerin toplam uzunluğu

    Requires:
        numpy as np
    """
    total_len = 0 # toplam uzunluk başlangıç değeri

    # 1. Üzerinde kolon bulunan düğümler
    col_constrained = set(np.where(colTopo == 1)[0]) | set(spans[colSpanTopo == 1].ravel())

    # 2. Aktif kirişlerin uç düğümleri
    beam_nodes = spans[beamTopo == 1].ravel().tolist()

    for i in np.where(beamTopo == 1)[0]:
        n1, n2 = spans[i]

        # n1 ve n2 kolonlar tarafından tutulu mu?
        n1_constrained, n2_constrained = n1 in col_constrained, n2 in col_constrained
        
        # 4. Eğer kirişin her iki ucunda da kolon varsa devam et;
        #    diğer kontrollere gerek yok, False kalacak.
        if n1_constrained and n2_constrained: continue

        # 5. Kirişin kendi uç düğümleri hariç diğer kirişlerin bağlı olduğu düğümler
        other_beam_nodes = beam_nodes.copy()
        # n1'i ve n2'yi yalnızca BİRER KEZ çıkar
        other_beam_nodes.remove(n1)
        other_beam_nodes.remove(n2)

        # 6. Diğer kirişler de hesaba katıldığında n1 ve n2 tutulu mu? 
        n1_constrained = n1_constrained or (n1 in other_beam_nodes)
        n2_constrained = n2_constrained or (n2 in other_beam_nodes)

        # 7. Eğer her iki uç da tutulmuşsa toplam dışı bırak
        if n1_constrained and n2_constrained: continue

        # 8. En az bir ucu serbest → toplam uzunluğa ekle
        total_len += spanLen[i]

    return total_len





def build_data_penalty(cand, geoData, xls):
    """
    Çözüm adayının penalty (ceza) değerlerini hesaplar.

    Args:
        cand (list)    : Çözümün tasarım vektörü (manual_design_vector.md dosyasına bakınız)
        geoData (dict) : Yapının geometrik verileri (build_data_geometry'den gelir)
        xls (dict)     : read_XLS.read_XLS ile okunan ayarlar (xls) dosyası

    Returns:
        Çözüm adayının penalty (ceza) değerleri

    Requires:
        none
    """
    colTopo     = cand[0]
    colSpanTopo = cand[5]
    beamTopo    = cand[8]

    axNod       = geoData["axNod"]
    nodeDist    = geoData["nodeDist"]
    spans       = geoData["spans"]
    axSpan      = geoData["axSpan"]
    spanLen     = geoData["spanLen"]
    spanDistMin = geoData["spanDistMin"]
    spanDistMax = geoData["spanDistMax"]

    colDistMin    = xls["colDist"]["min"]
    colDistMax    = xls["colDist"]["max"]
    beamDistMin   = xls["beamDist"]["min"]
    beamDistMax   = xls["beamDist"]["max"]
    beamLenLimMin = xls["beamLenLim"]["min"]
    beamLenLimMax = xls["beamLenLim"]["max"]
    
    beam_lengths = build_penalty_beam_lengths(colTopo, colSpanTopo, beamTopo, axNod, nodeDist, axSpan, beamLenLimMin, beamLenLimMax)
    beam_dist = build_penalty_beam_dist(beamTopo, spanDistMin, spanDistMax, beamDistMin, beamDistMax)
    col_dist = build_penalty_col_dist(colTopo, colSpanTopo, nodeDist, spans, colDistMin, colDistMax)
    beam_with_free_end = build_penalty_beam_with_free_end(colTopo, colSpanTopo, beamTopo, spans, spanLen)
    
    return beam_lengths, beam_dist, col_dist, beam_with_free_end