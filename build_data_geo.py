import func_geo_basic as geoBasic
"""
Required by:
    build_nodes_axMat
    build_axNod
    build_polygons
    build_areaOnNod
    build_areaInNod
    build_areaInSpan
    build_data_geo
"""

import numpy as np
"""
Required by:
    build_nodAx
    build_nodeDist
    build_spans
    build_nodMat
    build_axSpan
    build_nodSpan
    build_spanAx
    build_spanLen
    build_spanDist
    build_polygonGA
    build_nodOnArea
    build_spanOnArea
    build_areaOnSpan
    build_areaInNod
    build_nodInArea
    build_areaInSpan
    build_spanInArea
"""

import shapely.geometry as shp
"""
Required by:
    build_nodes_axMat
    build_polygonGA
"""





def build_nodes_axMat(axes):
    """
    Verilen eksenleri kullanarak nodes ve axMat numpy dizilerini oluşturur.
    nodes dizisi eksenlerin kesişim noktalarının koordinatlarını içerir. axMat dizisi hangi
    eksen ile hangi eksenin kesişiminde hangi düğümün bulunduğunun bilgisini tutar.

    Args:
        axes (numpy.ndarray): Eksenlerin başlangıç ve bitiş noktalarını içeren numpy dizisi
                              (read_XLS.read_XLS ile oluşturulmalıdır)
    
    Returns:
        tuple: nodes ve axMat numpy dizilerini içeren bir tuple
    
    Requires:
        func_geo_basic as geoBasic
        shapely.geometry as shp
    """
    axes_lines = [shp.LineString(i) for i in axes]
    nodes, axMat = geoBasic.line_intersection(axes_lines)
    return nodes, axMat





def build_axNod(axes, axMat, nodes):
    """
    axes listesindeki akslar üzerindeki düğümlerin nodes listesindeki indekslerini döndürür.
    Eksenler üzerindeki düğümler, eksenin başlangıç noktasından bitiş noktasına doğru sıralıdır.

    Args:
        axes (numpy.ndarray): Eksenlerin başlangıç ve bitiş noktalarını içeren numpy dizisi
        axMat (numpy.ndarray): Eksenlerin kesişim noktalarında hangi düğümün bulunduğunu tutan
                               matrisi içeren numpy dizisi
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi
    
    Returns:
        numpy.ndarray: Eksenler üzerindeki düğümlerin indekslerini içeren numpy dizileri listesi
    
    Requires:
        func_geo_basic as geoBasic
    """
    axNod = []
    for i in range(len(axes)):
        axis_start = axes[i][0]
        axis_nodes = axMat[i][axMat[i] != -1]
        ordered_idx = geoBasic.order_points(nodes[axis_nodes], axis_start)
        ordered_nodes = axis_nodes[ordered_idx]
        axNod.append(ordered_nodes)
    return axNod





def build_nodAx(axNod, nodes):
    """
    nodes dizisindeki her bir düğümün hangi aksların kesişiminde bulunduğunu döndürür.

    Args:
        axNod: List of np.arrays, eksenler üzerindeki düğümlerin indeksleri
        nodes: Düğümlerin koordinatlarını içeren numpy dizisi

    Returns:
        List of np.arrays
    
    Requires:
        numpy
    """
    nodAx = [[] for _ in range(len(nodes))]

    for axis, axis_nodes in enumerate(axNod):
        for node in axis_nodes:
            nodAx[node].append(axis)

    nodAx = [np.array(indices, dtype=int) for indices in nodAx]
    return nodAx





def build_nodeDist(axNod, nodes):
    """
    nodes dizisindeki düğümler arasındaki mesafeleri bir matris olarak döndürür.
    eğer iki düğüm aynı aks üzerinde değilse, mesafe -1 olarak ayarlanır.

    Args:
        axNod: List of np.arrays, eksenler üzerindeki düğümlerin indeksleri
        nodes: Düğümlerin koordinatlarını içeren numpy dizisi

    Returns:
        numpy.ndarray: Düğümler arasındaki mesafeleri içeren matris
    
    Requires:
        numpy
    """
    N = len(nodes)
    nodeDist = np.full((N, N), -1) # Tüm değerleri -1 ile başlat

    for ax in axNod:
        if ax.size < 2: continue

        coords = nodes[ax]  # aks üzerindeki düğüm koordinatları
        diff = coords[:, None, :] - coords[None, :, :]  # tüm i-j farkları
        dist = np.linalg.norm(diff, axis=2)             # Öklidyen mesafe

        # Mesafeleri ilgili düğüm çiftlerine ata
        for idx_i in range(len(ax)):
            node_i = ax[idx_i]
            for idx_j in range(idx_i, len(ax)):
                node_j = ax[idx_j]
                d = dist[idx_i, idx_j]
                nodeDist[node_i, node_j] = d
                nodeDist[node_j, node_i] = d

    return nodeDist





def build_spans(axNod):
    """
    Akslar üzerindeki düğümleri kullanarak, aks parçalarının başlangıç ve bitiş düğümlerini
    içeren diziyi oluşturur.

    Args:
        axNod (list): List of np.arrays, eksenler üzerindeki düğümlerin indeksleri

    Returns:
        numpy.ndarray: Aks parçalarının başlangıç ve bitiş düğümlerini içeren numpy dizisi
    
    Requires:
        numpy
    """
    pairs = []
    for arr in axNod:
        if len(arr) >= 2:
            # [arr[0], arr[1]], [arr[1], arr[2]], ...
            pair = np.stack([arr[:-1], arr[1:]], axis=1)
            pairs.append(pair)
    spans = np.vstack(pairs)
    return spans





def build_nodMat(spans, nodes):
    """
    Düğümler arasındaki aks parçasının indeksini tutan matrisi oluşturur.
    Eğer iki düğüm aynı aks üzerinde değilse ilgili eleman -1 olarak ayarlanır.

    Args:
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini
                               içeren numpy dizisi
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi

    Returns:
        numpy.ndarray: Düğümler arasındaki aks parçasının indeksini tutan matris
    
    Requires:
        numpy
    """
    nodMat = np.full((len(nodes), len(nodes)), -1, dtype=int)
    for idx, (i, j) in enumerate(spans):
        nodMat[i, j], nodMat[j, i] = idx, idx
    return nodMat





def build_axSpan(axNod, nodMat):
    """
    Akslar üzerindeki düğümler arasındaki aks parçalarının indekslerini döndürür.
    Dikkate alınan düğümler, aksların başlangıç noktalarından bitiş noktalarına
    doğru sıralıdır.
    
    Args:
        axNod: List of np.arrays, eksenler üzerindeki düğümlerin indeksleri
        nodMat: Düğümler arasındaki aks parçasının indeksini tutan matris
    
    Returns:
        List of np.arrays
    
    Requires:
        numpy
    """
    axSpan = []
    for node_array in axNod:
        pairs = np.stack([node_array[:-1], node_array[1:]], axis=1)  # ardışık çiftler
        values = np.array([nodMat[i, j] for i, j in pairs])
        axSpan.append(values)
    return axSpan





def build_nodSpan(nodes, spans):
    """
    Her düğümün hangi aks parçasının bir sınırı olduğunu gösteren listeyi oluşturur.

    Args:
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren liste
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi
    
    Returns:
        list of np.arrays: Her düğüm için aks parçalarının indekslerini içeren liste
    
    Requires:
        numpy
    """
    nodSpan = [[] for _ in range(len(nodes))]
    
    for i, (a, b) in enumerate(spans):
        nodSpan[a].append(i)
        nodSpan[b].append(i)
    
    return [np.array(i) for i in nodSpan]





def build_spanAx(axSpan, spans):
    """
    spans dizisindeki her aks parçasının hangi aks üzerinde olduğunu gösteren numpy
    dizisini oluşturur.

    Args:
        axSpan (list of np.arrays): Akslar üzerindeki düğümler arasındaki aks parçalarının
                                    indeksleri
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi

    Returns:
        np.array: Her bir aks parçasının hangi aks üzerinde olduğu bilgisini içeren numpy
                  dizisi

    Requires:
        numpy
    """
    spanAx = np.full(len(spans), -1, dtype=int)  # Başta hepsi -1

    for i, arr in enumerate(axSpan):
        for val in arr:
            spanAx[val] = i  # span'ın ait olduğu array indeksi

    return spanAx





def build_spanLen(spans, nodeDist):
    """
    spans dizisindeki her aks parçasının uzunluğunu döndürür.

    Args:
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi
        nodeDist (numpy.ndarray): Düğümler arasındaki mesafeleri içeren matris
    
    Returns:
        numpy.ndarray: Aks parçalarının uzunluklarını içeren numpy dizisi
    
    Requires:
        numpy
    """
    spans = np.asarray(spans)
    spanLen = nodeDist[spans[:, 0], spans[:, 1]]
    return spanLen





def build_spansG(nodes, spans):
    """
    spans dizisindeki her aks parçasının orta nokta koordinatlarını döndürür.

    Args:
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi
    
    Returns:
        numpy.ndarray: Aks parçalarının orta nokta koordinatlarını içeren numpy dizisi
    
    Requires:
    
    """
    start_points = nodes[spans[:, 0]]
    end_points   = nodes[spans[:, 1]]
    spansG    = (start_points + end_points) / 2
    return spansG





def build_spanDist(spans, nodAx, nodeDist):
    """
    spans listesindeki aks parçaları arasındaki en küçük ve en büyük mesafeleri bulunduran
    iki matrisi döner. Eğer iki aks parçası arasında bir mesafeden söz edilemiyorsa, matrislerin
    ilgili elemanları -1 olarak ayarlanır.

    Args:
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi
        nodAx (list of numpy.ndarrays): Her bir düğümden geçen aksları içeren liste
        nodeDist (numpy.ndarray): Düğümler arasındaki mesafeleri içeren matris

    Returns:
        tuple of numpy.ndarrays: Aks parçaları arasındaki en küçük ve en büyük mesafeler

    Requires:
        numpy
    """
    n_spans     = len(spans)
    spanDistMin = np.full((n_spans, n_spans), -1, dtype=int)
    spanDistMax = np.full((n_spans, n_spans), -1, dtype=int)

    # node_a ile node_b aynı aks üzerinde mi? Kontrolünü yapan alt fonksiyon
    def same_axis(node_a, node_b):
        return len(set(nodAx[node_a]) & set(nodAx[node_b])) > 0

    for i in range(n_spans):
        for j in range(i+1, n_spans):
            s1_start, s1_end = spans[i]
            s2_start, s2_end = spans[j]

            # Eğer bir span'in her iki ucu ve diğer span'in en az bir ucu aynı aks üzerinde ise
            # bu span'ler arasında bir mesafeden söz edilemez.
            s1_axis = set(nodAx[s1_start]) & set(nodAx[s1_end])
            s2_axis = set(nodAx[s2_start]) & set(nodAx[s2_end])

            if s1_axis & set(nodAx[s2_start]) : continue
            if s1_axis & set(nodAx[s2_end])   : continue
            if s2_axis & set(nodAx[s1_start]) : continue
            if s2_axis & set(nodAx[s1_end])   : continue

            # İki span arasındaki mesafeyi hesapla
            matched = False
            dist1 = dist2 = -1

            # Senaryo 1 : Aynı yönlü bağlantı var
            if same_axis(s1_start, s2_start) and same_axis(s1_end, s2_end):
                dist1 = nodeDist[s1_start][s2_start]
                dist2 = nodeDist[s1_end][s2_end]
                matched = True

            # Senaryo 2 : Ters yönlü bağlantı var
            elif same_axis(s1_start, s2_end) and same_axis(s2_start, s1_end):
                dist1 = nodeDist[s1_start][s2_end]
                dist2 = nodeDist[s2_start][s1_end]
                matched = True

            # Bağlantı bulundu ise mesafeleri güncelle
            if matched and dist1 != -1 and dist2 != -1:
                minDist, maxDist  = min(dist1, dist2), max(dist1, dist2)
                spanDistMin[i][j] = spanDistMin[j][i] = minDist
                spanDistMax[i][j] = spanDistMax[j][i] = maxDist

    return spanDistMin, spanDistMax





def build_polygons(polygons_points, nodes):
    """
    Verilen poligon köşe koordinatlarının nodes dizisindeki indekslerini döndürür.

    Args:
        polygons_points (numpy.ndarray): Poligonların köşe koordinatları
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi

    Returns:
        list of np.arrays: Her poligon için köşe nokta indekslerini içeren liste
    
    Requires:
        func_geo_basic as geoBasic
    """
    return [geoBasic.point_indexes(i, nodes) for i in polygons_points]





def build_polygonGA(nodes, polygons):
    """
    Verilen poligonların geometrik merkezlerini ve alanlarını hesaplar.

    Args:
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi
        polygons (list of np.arrays): Poligonların köşe nokta indekslerini içeren liste

    Returns:
        tuple: Poligonların geometrik merkezlerini ve alanlarını içeren numpy dizileri
    
    Requires:
        numpy
        shapely.geometry as shp
    """
    polygons_G, polygons_A = [], []

    for polyNodes in polygons:
        polyShape = shp.Polygon(nodes[polyNodes])

        centroid = polyShape.centroid
        polygons_G.append([centroid.x, centroid.y])

        polygons_A.append(polyShape.area)

    return np.array(polygons_G), np.array(polygons_A)





def build_areaOnNod(axNod, areas):
    """
    areas dizisindeki alanlara ait kenarların hangi düğümlerin üzerinden geçtiğini döndürür.

    Args:
        axNod (list of np.arrays): Eksenler üzerindeki düğümlerin indeksleri
        areas (list of np.arrays): Poligonların köşe nokta indekslerini içeren liste

    Returns:
        list of np.arrays: Her alan için düğüm indekslerini içeren liste
    
    Requires:
        func_geo_basic as geoBasic
    """
    areaOnNod = [geoBasic.stations_multiple(axNod, area) for area in areas]
    return areaOnNod





def build_nodOnArea(areaOnNod, nodes):
    """
    nodes listesindeki düğümlerin hangi alanlara ait kenarların üzerinde bulunduğunu döndürür.

    Args:
        areaOnNod (list of np.arrays): Alanların üzerindeki düğümlerin indeksleri
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi

    Returns:
        list of np.arrays: Her düğüm için alan indekslerini içeren liste
    
    Requires:
        numpy
    """
    nodOnArea = [[] for _ in range(len(nodes))]

    for i, arr in enumerate(areaOnNod):
        for node in arr: nodOnArea[node].append(i)

    for idx, lst in enumerate(nodOnArea):
        if lst: nodOnArea[idx] = np.array(lst, dtype=int)
        else: nodOnArea[idx] = -1  # integer -1

    return nodOnArea





def build_spanOnArea(areaOnNod, spans):
    """
    spans dizisindeki aks parçalarının hangi alanlara ait kenarların üzerinde bulunduğunu
    döndürür.

    Args:
        areaOnNod (list of np.arrays): Alanların üzerindeki düğümlerin indeksleri
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi

    Returns:
        list of np.arrays: Her aks parçası için alan indekslerini içeren liste
    
    Requires:
        numpy
    """
    spanOnArea = []

    for a, b in spans:
        found_arrays = []

        for i, arr in enumerate(areaOnNod):
            arr = np.asarray(arr)
            if arr.size < 2: continue

            # Ardışık çiftler
            left, right = arr[:-1], arr[1:]

            # (a,b) veya (b,a) kontrolü
            cond = ((left == a) & (right == b)) | ((left == b) & (right == a))
            if np.any(cond): found_arrays.append(i)

        if found_arrays:
            spanOnArea.append(np.array(found_arrays))
        else:
            spanOnArea.append(-1)

    return spanOnArea





def build_areaOnSpan(spanOnArea, areas):
    """
    areas listesindeki alanların kenarlarının üzerinde hangi aks parçalarının bulunduğunu
    döndürür.

    Args:
        spanOnArea (list of np.arrays): Her aks parçası için alan indekslerini içeren liste
        areas (list of np.arrays): Alanların köşe nokta indekslerini içeren liste

    Returns:
        list of np.arrays: Her alan için aks parçalarının indekslerini içeren liste
    
    Requires:
        numpy
    """
    areaOnSpan = [[] for _ in range(len(areas))]

    for span_idx, area in enumerate(spanOnArea):
        if isinstance(area, int) and area == -1: continue
        for area_idx in area:
            areaOnSpan[area_idx].append(span_idx)
    
    areaOnSpan = [
        -1 if len(a) == 0 else np.array(a, dtype=int)
        for a in areaOnSpan
    ]
    
    return areaOnSpan





def build_areaInNod(areas, nodes, areaOnNod):
    """
    areas dizisindeki alanların içinde hangi düğümlerin bulunduğunu döndürür.

    Args:
        areas (list of np.arrays): Poligonların köşe nokta indekslerini içeren liste
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi
        areaOnNod (list of np.arrays): Alanların kenarları üzerindeki düğümlerin indeksleri

    Returns:
        list of np.arrays: Her alan için düğüm indekslerini içeren liste
    
    Requires:
        func_geo_basic as geoBasic
        numpy
    """
    all_nodes = np.arange(len(nodes))
    areaInNod = []

    for i, poly_nodes in enumerate(areas):
        test_nodes = np.setdiff1d(all_nodes, areaOnNod[i])
        inside_mask = geoBasic.nodes_in_polygon(test_nodes, poly_nodes, nodes)
        inside_nodes = test_nodes[inside_mask]
        areaInNod.append(inside_nodes)

    return areaInNod





def build_nodInArea(nodes, areaInNod):
    """
    nodes listesindeki düğümlerin hangi alanların içinde bulunduğunu döndürür.
    Bir düğüm hiçbir alanın içinde değilse -1 olarak ayarlanır.

    Args:
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi
        areaInNod (list of np.arrays): Alanların içindeki düğümlerin indeksleri

    Returns:
        list of np.arrays: Her düğüm için alan indekslerini içeren liste
    
    Requires:
        numpy
    """
    nodInArea = [[] for _ in range(len(nodes))]

    for area_idx, node_ids in enumerate(areaInNod):
        for node_id in node_ids:
            nodInArea[node_id].append(area_idx)

    nodInArea = [
        np.array(areas) if areas else -1
        for areas in nodInArea
    ]

    return nodInArea





def build_areaInSpan(polygons, nodes, spans, areaOnSpan):
    """
    areas listesindeki alanların içinde hangi aks parçalarının bulunduğunu döndürür.

    Args:
        polygons (list of np.arrays): Poligonların köşe nokta indekslerini içeren liste
        nodes (numpy.ndarray): Düğümlerin koordinatlarını içeren numpy dizisi
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi
        areaOnSpan (list of np.arrays): Her alanın kenarlarının üzerindeki aks parçalarının
                                        indeksleri

    Returns:
        list of np.arrays: Her alan için aks parçalarının indekslerini içeren liste
    
    Requires:
        numpy
        func_geo_basic as geoBasic
    """
    # Tüm çizgilerin orta noktalarını önceden hesapla
    all_span_ids = np.arange(len(spans))
    span_mids = (nodes[spans[:, 0]] + nodes[spans[:, 1]]) / 2
    areaInSpan = []

    for i, poly_nodes in enumerate(polygons):
        if len(poly_nodes) < 3:
            areaInSpan.append(np.array([], dtype=int))
            continue        

        # Bu poligon için test edilecek span indeksleri
        test_ids = np.setdiff1d(all_span_ids, areaOnSpan[i])

        # Test span’larının orta noktalarını al
        mids = span_mids[test_ids]

        # İçeride olanları test et
        inside_mask = geoBasic.nodes_in_polygon(mids, poly_nodes, nodes)
        inside_spans = test_ids[inside_mask]

        areaInSpan.append(inside_spans)
    
    return areaInSpan





def build_spanInArea(spans, areaInSpan):
    """
    spans dizisindeki aks parçalarının hangi alanların içinde bulunduğunu döndürür.

    Args:
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                               numpy dizisi
        areaInSpan (list of np.arrays): Her alan için aks parçalarının indekslerini içeren
                                        liste

    Returns:
        list of np.arrays: Her aks parçası için alan indekslerini içeren liste
    
    Requires:
        numpy
    """
    spanInArea = [[] for _ in range(len(spans))]

    for area_idx, span_ids in enumerate(areaInSpan):
        for span_id in span_ids:
            spanInArea[span_id].append(area_idx)

    # Şekli uygun hale getir (liste -> array veya -1)
    spanInArea = [
        np.array(indices) if indices else -1
        for indices in spanInArea
    ]
    return spanInArea





def build_data_geo(axes, basePol_points, floorPol_points, areas_points):
    """
    Planın temel geometrik verisini oluşturur.

    Args:
        axes (numpy.ndarray): Akslar
        basePol_points (numpy.ndarray): Oturma alanı poligonunun köşe nokta koordinatları
        floorPol_points (numpy.ndarray): Kat alanı poligonunun köşe nokta koordinatları
        areas_points (list of numpy.ndarrays): Alanların (hacimlerin) köşe nokta koordinatları
        -- Tamamı read_DXF.read_DXF ile okunur --
    
    Returns:
        dict of numpy.ndarrays: Temel geometrik veri
    
    Requires:
        func_geo_basic as geoBasic
    """
    axesDirection  = geoBasic.line_direction(axes)
    axesAngle      = geoBasic.line_angle(axes).T
    
    nodes, axMat   = build_nodes_axMat(axes)
    axNod          = build_axNod(axes, axMat, nodes)
    nodAx          = build_nodAx(axNod, nodes)
    nodeDist       = build_nodeDist(axNod, nodes)

    spans          = build_spans(axNod)
    nodMat         = build_nodMat(spans, nodes)
    axSpan         = build_axSpan(axNod, nodMat)
    nodSpan        = build_nodSpan(nodes, spans)
    spanAx         = build_spanAx(axSpan, spans)
    spanLen        = build_spanLen(spans, nodeDist)
    spansG         = build_spansG(nodes, spans)
    spanDistMin, spanDistMax = build_spanDist(spans, nodAx, nodeDist)

    basePol        = build_polygons(basePol_points, nodes)[0]
    floorPol       = build_polygons(floorPol_points, nodes)[0]
    areas          = build_polygons(areas_points, nodes)
    
    basePolGA      = build_polygonGA(nodes, [basePol])
    basePolG       = basePolGA[0][0]
    basePolA       = basePolGA[1][0]
    floorPolGA     = build_polygonGA(nodes, [floorPol])
    floorPolG      = floorPolGA[0][0]
    floorPolA      = floorPolGA[1][0]
    areasG, areasA = build_polygonGA(nodes, areas)

    nodesToFloorG  = geoBasic.normalized_distances(nodes, floorPolG)
    spansToFloorG  = geoBasic.normalized_distances(spansG, floorPolG)
    areasToFloorG  = geoBasic.normalized_distances(areasG, floorPolG)

    areaOnNod      = build_areaOnNod(axNod, areas)
    nodOnArea      = build_nodOnArea(areaOnNod, nodes)
    spanOnArea     = build_spanOnArea(areaOnNod, spans)
    areaOnSpan     = build_areaOnSpan(spanOnArea, areas)
    areaInNod      = build_areaInNod(areas, nodes, areaOnNod)
    nodInArea      = build_nodInArea(nodes, areaInNod)
    areaInSpan     = build_areaInSpan(areas, nodes, spans, areaOnSpan)
    spanInArea     = build_spanInArea(spans, areaInSpan)

    return {
        "axesDirection" : axesDirection,
        "axesAngle"     : axesAngle,

        "nodes"         : nodes,
        "axMat"         : axMat,
        "axNod"         : axNod,
        "nodAx"         : nodAx,
        "nodeDist"      : nodeDist,

        "spans"         : spans,
        "nodMat"        : nodMat,
        "axSpan"        : axSpan,
        "nodSpan"       : nodSpan,
        "spanAx"        : spanAx,
        "spanLen"       : spanLen,
        "spansG"        : spansG,
        "spanDistMin"   : spanDistMin,
        "spanDistMax"   : spanDistMax,

        "basePol"       : basePol,
        "floorPol"      : floorPol,
        "areas"         : areas,

        "basePolG"      : basePolG,
        "basePolA"      : basePolA,
        "floorPolG"     : floorPolG,
        "floorPolA"     : floorPolA,
        "areasG"        : areasG,
        "areasA"        : areasA,

        "nodesToFloorG" : nodesToFloorG,
        "spansToFloorG" : spansToFloorG,
        "areasToFloorG" : areasToFloorG,
        
        "areaOnNod"     : areaOnNod,
        "nodOnArea"     : nodOnArea,
        "spanOnArea"    : spanOnArea,
        "areaOnSpan"    : areaOnSpan,
        "areaInNod"     : areaInNod,
        "nodInArea"     : nodInArea,
        "areaInSpan"    : areaInSpan,
        "spanInArea"    : spanInArea
    }