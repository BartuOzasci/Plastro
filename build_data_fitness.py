import numpy as np
"""
Required by:
    build_fitness_span_in_area
    build_fitness_node_in_area
    build_fitness_standalone_beams
    build_fitness_crossing_beams
    build_data_fitness
"""





def build_fitness_span_in_area(spanLen, spanInArea, areaImportance):
    """
    Sistemde her bir aks parçasında çizgisel kolon veya kiriş bulunmasının ne kadar
    "alan ihlali" uygunsuzluğuna sebep olduğunu hesaplar.

    Args:
        spanLen (np.ndarray)        : Her bir aks parçasının uzunluğunu içeren dizi
        spanInArea (list)           : Her bir aks parçasının hangi alanların içinde
                                      bulunduğu bilgisini içeren liste
        areaImportance (np.ndarray) : Her bir alanın önem derecesini içeren dizi
                                      slabProp["importance"]

    Returns:
        Sistemde her bir aks parçasında çizgisel kolon veya kiriş bulunmasının ne kadar
        "alan ihlali" uyzgunsuzluğuna sebep olduğunu gösteren numpy dizisi

    Requires:
        numpy
    """
    # Boş dizi oluştur
    fitness = np.zeros(len(spanInArea), dtype=float)

    # Açıklık uygunsuzluğunu hesapla
    for i, areas in enumerate(spanInArea):
        if isinstance(areas, (int, np.integer)) and areas == -1:
            fitness[i] = 0
        else:
            fitness[i] = spanLen[i] * np.sum(areaImportance[areas])

    # Açıklık uygunsuzluğunu döndür
    return fitness





def build_fitness_node_in_area(nodInArea, areaImportance):
    """
    Sistemde her bir düğümde noktasal kolon bulunmasının ne kadar "alan ihlali"
    uygunsuzluğuna sebep olduğunu hesaplar.

    Args:
        nodInArea (list)            : Her bir düğümün hangi alanların içinde bulunduğunu
                                      içeren liste
        areaImportance (np.ndarray) : Her bir alanın önem derecesini içeren dizi
                                      slabProp["importance"]

    Returns:
        Sistemde her bir düğümde noktasal kolon bulunmasının ne kadar "alan ihlali"
        uygunsuzluğuna sebep olduğunu gösteren numpy dizisi

    Requires:
        numpy
    """
    # Boş liste oluştur
    fitness = []
    
    for areas in nodInArea:
        if isinstance(areas, np.ndarray) and areas.size > 0:
            fitness.append(areaImportance[areas].sum())
        else:
            fitness.append(0)

    return np.array(fitness, dtype=float)





def build_fitness_standalone_beams(beamTopo, contBeamTopo, contBeam, spanLen):
    """
    ONDEMAND : Sistemde bulunan ve yine sistemde bulunan bir sürekli hattın parçası olmayan
    bağımsız kirişlerin toplam uzunluğunu hesaplar.

    Args:
        beamTopo (np.ndarray)     : Sistemde bulunan kirişların topolojisi
        contBeamTopo (np.ndarray) : Sistemde bulunan sürekli hatların topolojisi
        contBeam (list)           : Sürekli hat bilgisi (build_contBeam'den gelir)
        spanLen (np.ndarray)      : Her bir aks parçasının uzunluğunu içeren dizi

    Returns:
        Sistemde bulunan ve yine sistemde bulunan bir sürekli hattın parçası olmayan
        bağımsız kirişlerin toplam uzunluğu

    Requires:
        numpy
    """
    # 1. Sistem içinde olan kirişlerin indeksleri
    active_beams = np.where(beamTopo == 1)[0]
    
    # 2. Sistem içinde olan sürekli hatların indeksleri
    active_contBeams = np.where(contBeamTopo == 1)[0]
    
    # 3. Bu hatlardaki kirişlerin birleşimi
    beams_in_cont = set()
    for idx in active_contBeams:
        beams_in_cont.update(contBeam[idx]["beam"])
    
    # 4. Bağımsız kirişleri bul
    standalone_beams = [b for b in active_beams if b not in beams_in_cont]
    
    # 5. Toplam uzunluğu hesapla
    fitness = spanLen[standalone_beams].sum() if standalone_beams else 0

    return fitness





def build_fitness_crossing_beams(
    colTopo, colSpanTopo, beamTopo, spans, nodSpan, spanAx, spanLen):
    """
    ONDEMAND : Kolon bulunmayan düğümlere saplanan kirişlerin toplam uzunluğunu hesaplar.
    Kirişler tüm sağlandığı düğümlerde değerlendirilir.

    Args:
        colTopo (np.ndarray)      : Sistemde bulunan noktasal kolonların topolojisi
        colSpanTopo (np.ndarray)  : Sistemde bulunan çizgisel kolonların topolojisi
        beamTopo (np.ndarray)     : Sistemde bulunan kirişların topolojisi
        spans (np.ndarray)        : Her bir aks parçasının bağlı olduğu düğümleri içeren dizi
        nodSpan (list)            : Her bir düğümün bağlı olduğu aks parçalarını içeren liste
        spanAx (np.ndarray)       : Her bir aks parçasının üzerinde bulunduğu aksı içeren dizi
        spanLen (np.ndarray)      : Her bir aks parçasının uzunluğunu içeren dizi

    Returns:
        Kolon bulunmayan düğümlere saplanan kirişlerin toplam uzunluğu

    Requires:
        numpy
    """
    # 1. Noktasal kolonların bağlı olduğu düğümleri çıkar
    mask_no_col = np.ones(len(colTopo), dtype=bool)
    mask_no_col[colTopo == 1] = False

    # 2. Çizgisel kolonların bağlı olduğu düğümleri çıkar
    col_span_nodes = np.unique(spans[colSpanTopo == 1].ravel())

    # 3. Çizgisel kolonların bağlı olduğu düğümleri de maskeye işle
    mask_no_col[col_span_nodes] = False
    
    # 4. Kolon bağlı olmayan düğümlerin indeksleri
    nodes_no_col = np.where(mask_no_col)[0]

    # 5. En az iki farklı aks üzerinde kiriş bağlanan düğümlere bağlanan
    # kirişlerin toplam uzunluğu
    fitness = 0
    for node in nodes_no_col:
        spans_connected = nodSpan[node]
        active_spans    = spans_connected[beamTopo[spans_connected] == 1]
        if active_spans.size >= 2:
            if np.unique(spanAx[active_spans]).size >= 2:
                fitness += spanLen[active_spans].sum()

    return fitness





def build_data_fitness(cand, geoData, contBeam,
        fitness_span_in_area, fitness_node_in_area):
    """
    Çözüm adayının fitness değerlerini hesaplar.

    Args:
        cand (list)    : Çözümün tasarım vektörü (manual_design_vector.md dosyasına bakınız)
        geoData (dict) : Yapının geometrik verileri (build_data_geometry'den gelir)
        contBeam (list): Olası sürekli kiriş hatları bilgisi (build_data_contBeam'den gelir)
        fitness_span_in_area (np.ndarray): build_fitness_span_in_area fonksiyonuna bakınız
        fitness_node_in_area (np.ndarray): build_fitness_node_in_area fonksiyonuna bakınız

    Returns:
        Çözüm adayının fitness değerleri

    Requires:
        numpy as np
    """
    colTopo      = cand[0]
    colSpanTopo  = cand[5]
    beamTopo     = cand[8]
    contBeamTopo = cand[11]

    spans   = geoData["spans"]
    nodSpan = geoData["nodSpan"]
    spanAx  = geoData["spanAx"]
    spanLen = geoData["spanLen"]

    span_in_area     = np.sum((colSpanTopo + beamTopo)* fitness_span_in_area)
    node_in_area     = np.sum(colTopo * fitness_node_in_area)
    standalone_beams = build_fitness_standalone_beams(beamTopo, contBeamTopo, contBeam, spanLen)
    crossing_beams   = build_fitness_crossing_beams(colTopo, colSpanTopo, beamTopo, spans, nodSpan, spanAx, spanLen)
    
    return span_in_area, node_in_area, standalone_beams, crossing_beams