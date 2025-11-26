"""
ALGORİTMA:

1. Bir poligon ve içindeki bir nokta bulutu simetrik ise, simetri eksen(ler)inin
   ilk noktası poligonun geometrik merkezidir.
2. Simetri eksen(ler)inin ikinci noktası ise ya poligonun köşe noktaları ya da
   poligonun kenarlarının ortasıdır.
3. Yukarıdaki esaslar ile önce poligonun "olası" simetri eksenleri tespit edilir.
4. Daha sonra sadece poligonun bu "olası" simetri eksenlerine göre simetrik olup
   olmadığı test edilir.
5. Eğer poligon için ilgili eksen(ler)e göre simetri bulundu ise, nokta bulutu da
   ilgili eksen(ler)e göre simetri için test edilir.
6. Hem poligonun hem de nokta bulutunun simetrik olduğu simetri eksen(ler)i ve
   nokta bulutunun simetrik eşlerinin olduğu listeler döndürülür.
"""





import numpy as np
"""
Required by:
    find_symmetry_points
    find_symmetry_indices
    find_axesToTestForSymmetry
    build_axesAndNodeSymmetry
    build_axesSymmetry
    build_spanSymmetry
    build_areaSymmetry
    build_nodeSymMove
    build_spanSymMove
    combine_symmetry_lists
"""

import shapely.geometry as shp
"""
Required by:
    find_axesToTestForSymmetry
"""

import func_geo_basic as geoBasic
"""
Required by:
    build_data_geo_symmetry
"""





def find_symmetry_points(points, symmetry_line):
    """
    Noktaları verilen simetri çizgisine göre yansıtarak simetri noktalarını bulur.

    Args:
        points (numpy.ndarray): Yansıtılacak noktaların koordinatları ([[x1,y1],[x2,y2],...])
        symmetry_line (numpy.ndarray): Simetri çizgisini tanımlayan iki nokta ([[x1,y1],[x2,y2]])
    
    Returns:
        numpy.ndarray: Yansıtılmış noktaların koordinatları ([[x1,y1],[x2,y2],...])

    Requires:
        numpy
    """
    A, B         = symmetry_line
    AB           = B - A
    AB_unit      = AB / np.linalg.norm(AB)
    AP           = points - A
    proj_lengths = AP @ AB_unit
    foot         = A + np.outer(proj_lengths, AB_unit)
    return 2 * foot - points





def find_symmetry_indices(points, symmetry_line, tol = 1e-6):
    """
    Noktaların symmetry_line eksenine göre simetriğinde bulunan noktaların points dizisindeki indekslerini döndürür.
    Eğer simetri yoksa "False" döner.

    Args:
        points (numpy.ndarray): Simetrisi kontrol edilecek noktaların koordinatları ([[x1,y1],[x2,y2],...])
        symmetry_line (numpy.ndarray): Simetri çizgisini tanımlayan iki nokta ([[x1,y1],[x2,y2]])
        tol (float, optional): Eşleşme toleransı

    Returns:
        numpy.ndarray veya bool: Simetri indeksleri veya "False"

    Requires:
        numpy
        find_symmetry_points
    """
    reflected = find_symmetry_points(points, symmetry_line)
    indices   = np.full(len(points), -1, dtype=int)

    for i, r in enumerate(reflected):
        if not indices[i] == -1: continue # i noktası zaten eşleştirilmiş

        # nokta simetri doğrusu üzerindeyse kendisiyle eşleşir
        if np.linalg.norm(points[i] - r) <= tol:
            indices[i] = i
            continue

        dists      = np.linalg.norm(points - r, axis=1)
        dists[i]   = np.inf  # kendisiyle eşleşmeyi engellemek için
        within_tol = np.where(dists <= tol)[0]

        # bir nokta dahi eşleşmiyorsa sistem simetrik değildir.
        if within_tol.size == 0: return False  # hiçbir eşleşme yok

        j = within_tol[np.argmin(dists[within_tol])]
        
        # Eğer i noktasına "tol" toleransı dahilinde en yakın nokta olan j, daha önce
        # eşleştirilmişse (bu nasıl olabilir bilmiyorum ama) sistem simetrik değildir.
        if not indices[j] == -1: return False  # j zaten başka bir nokta ile eşleşmiş
        else                   : indices[i], indices[j] = j, i

    return indices





def find_axesToTestForSymmetry(polygon_nodes, points):
    """
    Düğüm noktaları verilen bir poligon için olası simetri eksenlerini döndürür.

    Args:
        polygon_nodes (numpy.ndarray): Poligonun düğüm noktaları (points dizisindeki indeksleri)
        points (numpy.ndarray): Düğüm noktası koordinatları ([[x1,y1],[x2,y2],...])

    Returns:
        numpy.ndarray: Olası simetri eksenleri

    Requires:
        shapely.geometry as shp
        numpy
    """
    # poligonun geometrik merkezi
    centroid = shp.Polygon(points[polygon_nodes]).centroid
    centroid = np.array([centroid.x, centroid.y])
    # olası simetri eksenleri için boş bir liste
    symmetry_lines = []

    # [1,3,6,1] gibi bir kapalı poligonda ilk nokta ile son nokta aynıdır.
    # İlk noktadan geçen eksen ile son noktadan geçen eksen aynı olduğu için
    # iki kez aynı eksen eklenmiş olur; ancak bu bir sorun değildir.
    for i in range(len(polygon_nodes) - 1):
        # olası simetri eksenleri poligonun geometrik merkezinden VE
        # köşe noktalarından VEYA kenar ortalarından geçebilir.
        p1, p2 = points[polygon_nodes[i]], points[polygon_nodes[i + 1]]
        midpoint = (p1 + p2) / 2
        
        symmetry_lines.append([centroid, p1])
        symmetry_lines.append([centroid, midpoint])
        symmetry_lines.append([centroid, p2])

    return np.array(symmetry_lines)





def build_axesAndNodeSymmetry(polygon_nodes, points, axesToTestForSymmetry):
    """
    Düğüm noktaları verilen bir poligon ve noktalar için axesToTestForSymmetry dizisindeki
    eksenleri test ederek simetri eksenlerini ve ilgili simetri eksenine göre points dizisinin
    simetrik indekslerini döndürür.

    Args:
        polygon_nodes (numpy.ndarray): Poligonun düğüm noktaları (points dizisindeki indeksleri)
        points (numpy.ndarray): Düğüm noktası koordinatları ([[x1,y1],[x2,y2],...])
        axesToTestForSymmetry (numpy.ndarray): Test edilecek olası simetri eksenleri

    Returns:
        list of numpy.ndarrays or bool: Simetri eksenleri ve noktaların simetrik indeksleri veya
        False, False

    Requires:
        numpy
        find_symmetry_indices
    """
    symmetry_axes, symmetry_nodes = [], []
    # poligonun köşe noktaları (ilk nokta ile son nokta aynı olduğu için son noktayı almıyoruz)
    polygon_points = points[polygon_nodes[:-1]]

    for sym_line in axesToTestForSymmetry:

        # olası simetri ekseni için POLİGON köşe noktalarının simetrik indekslerini bulmaya çalış
        sym_indices_polygon = find_symmetry_indices(polygon_points, sym_line)
        # Eğer simetri bulunamadıysa bu ekseni atla
        if sym_indices_polygon is False: continue

        # şimdi de NOKTA BULUTU için simetrik indeksleri bulmaya çalış
        sym_indices_point = find_symmetry_indices(points, sym_line)
        # Eğer simetri bulunamadıysa bu ekseni atla
        if sym_indices_point is False: continue

        # simetri ekseni bulundu ve noktaların bulunan simetrik indeksleri daha önce başka bir eksen
        # için bulunmadı ise ekseni ve simetrik indeksleri ilgili listelere ekle
        if not any(np.array_equal(sym_indices_point, x) for x in symmetry_nodes):
            symmetry_axes.append(sym_line)
            symmetry_nodes.append(sym_indices_point)

    # Eğer hiçbir simetri bulunamadıysa "False" döndür
    if not symmetry_nodes: return False, False
    else                 : return np.array(symmetry_axes), np.array(symmetry_nodes)





def build_axesSymmetry(axNod, nodeSymmetry):
    """
    Her simetri ekseni için simetrik aksları bulur.

    Args:
        axNod (list of np.ndarrays): Her aksın üzerinde bulunan düğüm indekslerini içeren liste
        nodeSymmetry (np.ndarray): Her simetri ekseni için düğüm simetri indekslerini içeren dizi

    Returns:
        np.ndarray: (k, n_axes), axesSymmetry[a, i] = j ⇒
                    a. simetri altında i. aks j. aksa simetriktir. Yoksa -1
    
    Requires:
        numpy
    """
    # Eğer düğüm simetri grubu "False" ise aks simetrisi yoktur.
    if nodeSymmetry is False: return False

    k = len(nodeSymmetry)
    n_axes = len(axNod)
    axesSymmetry = np.full((k, n_axes), -1, dtype=int)

    for a in range(k):
        for i in range(n_axes):
            
            if axesSymmetry[a, i] != -1: continue  # zaten eşleştirilmiş

            axis_i_nodes = axNod[i]
            sym_nodes_i = nodeSymmetry[a][axis_i_nodes]
            sym_nodes_i_sorted = np.sort(sym_nodes_i)

            for j in range(i + 1, n_axes):
                axis_j_nodes = axNod[j]
                if np.array_equal(sym_nodes_i_sorted, np.sort(axis_j_nodes)):
                    axesSymmetry[a, i] = j
                    axesSymmetry[a, j] = i
                    break

            # Eğer kendiyle simetrikse
            if axesSymmetry[a, i] == -1 and np.array_equal(sym_nodes_i_sorted, np.sort(axis_i_nodes)):
                axesSymmetry[a, i] = i

    return axesSymmetry





def build_spanSymmetry(spans, nodeSymmetry):
    """
    Aks parçalarının verilen düğüm noktası simetri gruplarına göre simetrik indekslerini bulur.

    Args:
        spans (numpy.ndarray): Simetrisi bulunacak aks parçaları
        nodeSymmetry (list of numpy.ndarrays): Düğüm noktalarına ait simetri grupları

    Returns:
        numpy.ndarray or bool: Aks parçalarının simetrik indeksleri veya False

    Requires:
        numpy
    """
    # Eğer düğüm simetri grubu "False" ise aks parçası simetrisi yoktur.
    if nodeSymmetry is False: return False
    
    spanSymmetry = []

    # Her simetri grubu için
    for nodeSymGroup in nodeSymmetry:
        # Simetrik span listesi oluştur
        symSpans = [
            [nodeSymGroup[span[0]], nodeSymGroup[span[1]]]
            for span in spans
        ]

        # Orijinal span'leri karşılaştırmak için sıralanmış tuple'lardan oluşan bir lookup sözlüğü
        span_set = {tuple(sorted(span)): i for i, span in enumerate(spans)}

        # Simetrik span'lerin indekslerini bul
        # Eğer düğüm simetrisi varsa her span'ın bir simetriği vardır. Yine de eğer simetrik span
        # bulunamazsa (ki bulunmalıdır) ilgili span'ın simetrik indeksi -1 döndürülür.
        sym_indices = [
            span_set.get(tuple(sorted(sym_span)), -1)
            for sym_span in symSpans
        ]

        spanSymmetry.append(np.array(sym_indices, dtype=int))
    
    return np.array(spanSymmetry)





def build_areaSymmetry(areas, nodeSymmetry):
    """
    Alanların verilen düğüm noktası simetri gruplarına göre simetrik indekslerini bulur.

    Args:
        areas (list of numpy.ndarrays): Simetrisi bulunacak alanlar
        nodeSymmetry (list of numpy.ndarrays): Düğüm noktalarına ait simetri grupları

    Returns:
        numpy.ndarray or bool: Alanların simetrik indeksleri veya False

    Requires:
        numpy
    """
    # Eğer düğüm simetri grubu "False" ise aks parçası simetrisi yoktur.
    if nodeSymmetry is False: return False

    areaSymmetry = []

    for nodeSymGroup in nodeSymmetry:
        # Alanların simetrik versiyonlarını oluştur
        symAreas = []
        for area in areas:
            symArea = [nodeSymGroup[areaNode] for areaNode in area]
            symAreas.append(symArea)

        # Karşılaştırma için sorted tuple => orijinal indeks
        area_set = {
            tuple(sorted(area.tolist())): i
            for i, area in enumerate(areas)
        }

        # Simetrik alanların indekslerini bul
        area_indices = []
        for sym_area in symAreas:
            key = tuple(sorted(sym_area))
            index = area_set.get(key, -1)
            area_indices.append(index)

        areaSymmetry.append(np.array(area_indices, dtype=int))

    return np.array(areaSymmetry)





def build_nodeSymMove(symAxesAngle):
    """
    Her simetri ekseni için x ve y yönündeki birim hareketlerin yansıma vektörlerini hesaplar.
    
    Args:
        symAxesAngle (np.ndarray): shape = (N, 3), her satır [theta, sin(theta), cos(theta)]
    
    Returns:
        np.ndarray: shape = (N, 2, 2)
            output[i, 0] = x yönünde birim hareketin yansıması (vektör)
            output[i, 1] = y yönünde birim hareketin yansıması (vektör)
    
    Requires:
        numpy
    """
    sin_theta, cos_theta = symAxesAngle[:, 1], symAxesAngle[:, 2]
    n = np.stack([cos_theta, sin_theta], axis=1)

    vx, vy = np.array([1.0, 0.0]), np.array([0.0, 1.0])
    dot_x, dot_y = np.dot(n, vx), np.dot(n, vy)

    vx_reflected = 2 * dot_x[:, np.newaxis] * n - vx  # (N, 2)
    vy_reflected = 2 * dot_y[:, np.newaxis] * n - vy  # (N, 2)

    nodeSymMove = np.stack([vx_reflected, vy_reflected], axis=1)  # (N, 2, 2)
    return nodeSymMove





def build_spanSymMove(nodes, spans, spanSymmetry, symAxesAngle):
    """
    symAxesAngle ile bilgileri verilen tüm simetri eksenleri için, spanSymmetry ile simetri bilgileri
    verilen aks parçaları kendi eksenlerine dik pozitif bir hareket yaptıklarında simetrisinde bulunan
    aks parçalarının (simetrinin korunması için) hangi işaretli hareketi yapmaları gerektiğini hesaplar.

    Args:
        nodes (ndarray): (n_nodes, 2) düğüm koordinatları
        spans (ndarray): (n_spans, 2) aks parçalarının başlangıç ve bitiş düğümleri
        spanSymmetry (ndarray): (n_axes, n_spans), aks parçalarının simetrik indeksleri dizisi
        symAxesAngle (ndarray): (n_axes, 3), simetri ekseni bilgileri [theta, sin(theta), cos(theta)]

    Returns:
        ndarray: (n_axes, n_spans), aks parçalarının hareket simetri bilgileri

    Requires:
        numpy
    """
    n_axes, n_spans = spanSymmetry.shape
    spanSymMove = np.zeros((n_axes, n_spans))

    for a in range(n_axes):
        sin_theta, cos_theta = symAxesAngle[a, 1], symAxesAngle[a, 2]
        n = np.array([cos_theta, sin_theta])  # simetri ekseninin birim vektörü

        for i in range(n_spans):
            # 1. Orijinal span ve sağ yön birim vektörü
            A, B = nodes[spans[i, 0]], nodes[spans[i, 1]]
            AB = B - A
            AB_unit = AB / np.linalg.norm(AB)
            normal = np.array([AB_unit[1], -AB_unit[0]])

            # 2. Hareketin simetri eksenine göre yansıması
            reflected_normal = 2 * np.dot(normal, n) * n - normal

            # 3. Simetrik span sağ yön birim vektörü
            sym_index = spanSymmetry[a, i]
            if sym_index == -1: continue  # simetriği yoksa atla

            A2, B2 = nodes[spans[sym_index, 0]], nodes[spans[sym_index, 1]]
            AB2 = B2 - A2
            AB2_unit = AB2 / np.linalg.norm(AB2)
            normalSym = np.array([AB2_unit[1], -AB2_unit[0]])

            # 4. Yansıyan hareketin simetriğindeki span yönüne izdüşümü
            spanSymMove[a, sym_index] = np.dot(reflected_normal, normalSym)

    return spanSymMove





def combine_symmetry_lists(sym_list):
    """
    Verilen bir nodeSymmetry, spanSymmetry veya areaSymmetry listesindeki simetrik
    indeksleri birleştirir.

    Args:
        sym_list (list of numpy.ndarrays): Simetrik indekslerin listesi

    Returns:
        lists of numpy.ndarrays: Birleştirilmiş simetrik indekslerin listesi

    Requires:
        numpy
    """
    # sym_list elemanları uniform olduğu için numpy array'e çevrilebilir.
    sym_list = np.array(sym_list)

    # m: kaç adet array var, n: her array kaç elemanlı
    m, n = sym_list.shape

    combined_list = []
    for i in range(n):
        combined = [sym_list[j, i] for j in range(m) if sym_list[j, i] != -1]
        combined_list.append(np.array(combined) if combined else -1)

    return combined_list





def build_data_geo_symmetry(polygon_nodes, nodes, axNod, spans, areas):
    """
    Verilen bir poligon ve düğüm noktaları bulutu için, düğüm noktalarının, aks parçalarının
    ve alanların simetrik indeks listelerini oluşturur.

    Args:
        polygon_nodes (numpy.ndarray): Poligonun köşe noktalarının indeksleri
        nodes (numpy.ndarray): Düğüm noktalarının koordinatları
        spans (numpy.ndarray): Aks parçalarının başlangıç ve bitiş noktalarının indeksleri
        areas (list of numpy.ndarrays): Alanların köşe noktalarının indeksleri
    
    Returns:
        dict of numpy.ndarrays: Simetri eksenleri, simetrik indeks listeleri ve simetrik hareket
                                bilgileri
    
    Requires:
        func_geo_basic as geoBasic
    """
    testForSymmetry = find_axesToTestForSymmetry(polygon_nodes, nodes)
    symmetryAxes, nodeSymmetry = build_axesAndNodeSymmetry(polygon_nodes, nodes, testForSymmetry)
    axesSymmetry = build_axesSymmetry(axNod, nodeSymmetry)
    spanSymmetry = build_spanSymmetry(spans, nodeSymmetry)
    areaSymmetry = build_areaSymmetry(areas, nodeSymmetry)
    
    if symmetryAxes is False:
        symmetryAxes = []
        symAxesAngle = []
        axesSymmetry = []
        nodeSymmetry = []
        spanSymmetry = []
        areaSymmetry = []
        nodeSymMove  = []
        spanSymMove  = []
    else:
        symAxesAngle = geoBasic.line_angle(symmetryAxes).T
        nodeSymMove  = build_nodeSymMove(symAxesAngle)
        spanSymMove  = build_spanSymMove(nodes, spans, spanSymmetry, symAxesAngle)
    
    # Bu "combine" işinden vazgeçtim; gereksiz.
    """
    nodeSymmetry = [] if nodeSymmetry is False else combine_symmetry_lists(nodeSymmetry)
    ...
    """

    return {
        "symmetryAxes" : symmetryAxes,
        "symAxesAngle" : symAxesAngle,

        "axesSymmetry" : axesSymmetry,
        "nodeSymmetry" : nodeSymmetry,
        "spanSymmetry" : spanSymmetry,
        "areaSymmetry" : areaSymmetry,
        
        "nodeSymMove"  : nodeSymMove,
        "spanSymMove"  : spanSymMove
    }