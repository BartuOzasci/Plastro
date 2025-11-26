import shapely.geometry as shp
"""
Required by:
    nodes_in_polygon
"""

import numpy as np
"""
Required by:
    line_direction
    line_angle
    line_intersection
    order_points
    point_indexes
    points_on_spans
    normalized_distances
    stations_single
    stations_multiple
    repair_polygon
    nodes_in_polygon
"""





def line_direction(lines):
    """
    Çizgilerin biribirine göre yönlerini belirler.
    
    Args:
        lines (numpy.ndarray): Çizgilerin başlangıç ve bitiş noktalarını içeren numpy dizisi
                               [ [[x1,y1],[x2,y2]] , [[x3,y3],[x4,y4]] , ... ]
        
    Returns:
        np.ndarray: (N, N) boyutunda yön matrisi; 1 (aynı), -1 (zıt), 0 (ortogonal ya da belirsiz)
    
    Requires:
        numpy
    """
    vectors = lines[:, 1] - lines[:, 0] # çizgi vektörleri
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) # vektörlerin normları (uzunlukları)
    norms[norms == 0] = 1 # uzunluğu (normu) 0 olanların normunu 1 yaparak sıfıra bölmeyi engelle
    unit_vectors = vectors / norms # normalize (birim) vektörler

    # Birim vektör matrisinin ve transpozunun noktasal çarpımı
    dot_products = np.dot(unit_vectors, unit_vectors.T)

    # Çizgilerinin birbirine göre yönlerini tutan matris
    # 1: aynı yön, -1: zıt yön, 0: dik ya da belirsiz
    directions = np.zeros((len(lines), len(lines)), dtype=int)
    directions[dot_products >  np.cos(np.deg2rad(90))] =  1  # aynı yön
    directions[dot_products < -np.cos(np.deg2rad(90))] = -1  # zıt yön
    
    return directions





def line_angle(lines):
    """
    Verilen çizgilerin açılarını ve açıların sin ve cos değerlerini hesaplar.

    Args:
        lines (numpy.ndarray): Çizgilerin başlangıç ve bitiş noktalarını içeren numpy dizisi
                               [ [[x1,y1],[x2,y2]] , [[x3,y3],[x4,y4]] , ... ]
    
    Returns:
        numpy.ndarray (shape=(3, N)):
            - Çizgi açılarını içeren numpy dizisi
            - Çizgi açılarına karşılık gelen sinüs değerlerini içeren numpy dizisi
            - Çizgi açılarına karşılık gelen kosinüs değerlerini içeren numpy dizisi
    
    Requires:
        numpy
    """
    vecs = lines[:, 1] - lines[:, 0]  # (dx, dy)
    angles = np.arctan2(vecs[:, 1], vecs[:, 0])
    return np.array([angles, np.sin(angles), np.cos(angles)])





def line_intersection(lines):
    """
    Verilen çizgiler arasındaki kesişim noktalarını bulur ve bu noktaları bir matris olarak döndürür.
    
    Args:
        lines (list): shapely.geometry.LineString nesneleri listesi

    Returns:
        points (numpy.ndarray): Kesişim noktalarının koordinatlarını içeren bir numpy dizisi
        pointMatrix (numpy.ndarray): Çizgilerin kesişim noktalarının indekslerini içeren bir numpy matrisi
    
    Requires:
        numpy
    """
    n_lines     = len(lines)
    pointMatrix = np.full((n_lines, n_lines), -1, dtype=int)
    points      = []

    for i in range(n_lines):
        for j in range(i+1, n_lines):
            if lines[i].intersects(lines[j]) is False: continue
            
            intersection = lines[i].intersection(lines[j])
            
            if intersection.geom_type == "Point":
                points.append([intersection.x, intersection.y])
                pointMatrix[i][j] = len(points) - 1
                pointMatrix[j][i] = len(points) - 1
    
    return np.array(points), pointMatrix





def order_points(points, ref_point):
    """
    Verilen noktaların, verilen referans noktasına uzaklıklarına göre sıralı indekslerini döndürür.
    
    Args:
        points (numpy.ndarray): Sıralanacak noktaların koordinatlarını içeren numpy dizisi
                                [ [x1,y1], [x2,y2], ... ]
        ref_point (numpy.ndarray): Referans noktasının koordinatları [x, y]

    Returns:
        numpy.ndarray: Noktaların referans noktasına uzaklıklarına göre sıralı indeksleri

    Requires:
        numpy
    """
    dists = np.linalg.norm(points - ref_point, axis=1)
    return np.argsort(dists)





def point_indexes(points, ref_points, tol=1e-6):
    """
    Verilen noktalara en yakın referans noktalarının indekslerini bulur.

    Args:
        points (numpy.ndarray): Sorgulanan noktaların koordinatlarını içeren numpy dizisi
        ref_points (numpy.ndarray): Referans noktalarının koordinatlarını içeren numpy dizisi
        tol (float, optional): Uzaklık toleransı

    Returns:
        numpy.ndarray: Verilen noktalara en yakın referans noktalarının indekslerini içeren numpy dizisi
    
    Requires:
        numpy
    """
    diffs = points[:, np.newaxis, :] - ref_points[np.newaxis, :, :]
    dists = np.linalg.norm(diffs, axis=2)

    min_indices = np.argmin(dists, axis=1)
    min_dists = np.min(dists, axis=1)

    indexes = np.full(len(points), -1, dtype=int)
    within_tol = min_dists <= tol
    indexes[within_tol] = min_indices[within_tol]

    return indexes





def points_on_spans(points, nodes, spans, tol=1e-6):
    """
    Verilen noktaların hangi aks parçalarının (tol toleransı ile) üzerinde olduğunu bulur.

    Args:
        points (np.ndarray)   : Noktaların koordinatlarını içeren numpy dizisi
        nodes (np.ndarray)    : Düğümlerin koordinatlarını içeren numpy dizisi
        spans (np.ndarray)    : Aks parçalarının başlangıç ve bitiş düğümlerini
                                içeren numpy dizisi        
        tol (float, optional) : Uzaklık toleransı

    Returns:
        np.ndarray : points dizindeki her bir noktanın hangi aks parçası üzerinde
                     olduğunu belirten dizi. Eğer nokta hiçbir aks parçası üzerinde
                     değilse ilgili indeksteki değer -1 olur.

    Requires:
        numpy as np
    """
    on_span = []
    
    for p in points:
        found = -1
        
        for i, (s, e) in enumerate(spans):
            a, b = nodes[s], nodes[e]
            ab, ap = b - a, p - a
            
            # noktanın span üzerindeki izdüşümünün bağıl konumu
            t = np.dot(ap, ab) / np.dot(ab, ab)
            
            if 0 <= t <= 1:
                proj = a + t * ab
                dist = np.linalg.norm(p - proj)
                if dist <= tol:
                    found = i
                    break  # ilk bulduğu span'i döndürüyor
        
        on_span.append(found)
    
    return np.array(on_span)





def normalized_distances(nodes, ref_point):
    """
    Noktaların bir referans noktasına olan normalize mesafelerini hesaplar.

    Args:
        nodes (numpy.ndarray)     : Noktaların koordinatlarını içeren numpy dizisi
        ref_point (numpy.ndarray) : Referans noktasının koordinatları

    Returns:
        np.ndarray : En büyük mesafe 1 olacak şekilde normalize edilmiş mesafeler
    
    Requires:
        numpy
    """
    # Mesafeleri hesapla
    distances = np.linalg.norm(nodes - ref_point, axis=1)

    # Maksimum mesafe ile normalize et (0'a bölme kontrolü ile)
    max_dist = np.max(distances)
    if max_dist == 0 : return np.zeros_like(distances)
    else             : return distances / max_dist





def stations_single(paths, route):
    """
    Verilen bir yollar listesinden, belirli bir rotanın başlangıç ve bitiş düğümleri arasındaki
    istasyonları bulur.

    Args:
        paths (list): Yollar listesini içeren liste [[p1,p2,p3,p4,...],[p5,p6,p7,p8,...],...]
        route (numpy.ndarray): Başlangıç ve bitiş düğümlerini içeren numpy dizisi [pA,pB]

    Returns:
        numpy.ndarray or bool: İlgili istasyonları içeren numpy dizisi veya False
    
    Requires:
        numpy
    """
    a, b = route
    for path in paths:
        if a in path and b in path:
            idx_a = np.where(path == a)[0][0]
            idx_b = np.where(path == b)[0][0]
            stations = path[idx_a:idx_b+1] if idx_a <= idx_b else path[idx_b:idx_a+1][::-1]
            return stations
    return False





def stations_multiple(paths, routes):
    """
    Verilen bir yollar listesinden, verilen rotaların başlangıç ve bitiş düğümleri arasındaki
    istasyonları bulur.

    Args:
        paths (list): Yollar listesi
        routes (numpy.ndarray): Rota üzerindeki istasyonların listesi

    Returns:
        numpy.ndarray: İlgili istasyonları içeren numpy dizisi

    Requires:
        numpy
        stations_single
    """
    stations = []

    for route in zip(routes[:-1], routes[1:]):
        stations_on_path = stations_single(paths, np.array(route))
        if stations_on_path.size > 0: # Bu sınama stations_on_path==False olsa da hata fırlatmaz
            # Eğer önceki stations_on_path'in sonu, yeni stations_on_path'in başı ile aynıysa tekrar ekleme
            if stations and stations[-1] == stations_on_path[0]:
                stations_on_path = stations_on_path[1:]
            stations.extend(stations_on_path)
        else:
            # Eğer stations_on_path bulunamazsa, sadece ilk düğümü ekle (tekrar eklememek için kontrol)
            if not stations or stations[-1] != route[0]: stations.append(route[0])

    # Son düğümü ekle
    if not stations or stations[-1] != routes[-1]: stations.append(routes[-1])
    return np.array(stations, dtype=routes.dtype)





def repair_polygon(polygon_nodes, nodes_on_lines):
    """
    Polygon_nodes içinde bulunan düğümleri, en fazla iki ardışık düğüm aynı çizgide olacak şekilde temizler.

    Args:
        polygon_nodes (numpy.ndarray): Poligonun düğümlerini içeren numpy dizisi
        nodes_on_lines (list): Her çizgi için düğüm indekslerini içeren numpy dizileri listesi
    
    Returns:
        numpy.ndarray: Temizlenmiş poligon düğümlerini içeren numpy dizisi

    Requires:
        numpy
    """
    to_remove = set()

    for group in nodes_on_lines:
        # Bu gruptaki hangi düğümler poligon içinde var?
        present = np.isin(group, polygon_nodes)
        present_nodes = group[present]

        # Eğer poligon içinde ardışık 3+ düğüm varsa, ara düğümler çıkarılır
        if len(present_nodes) >= 3:
            to_remove.update(present_nodes[1:-1])

    # Düğüm sırasını koruyarak silinecekleri çıkar
    mask = np.isin(polygon_nodes, list(to_remove), invert=True)
    return polygon_nodes[mask]





def nodes_in_polygon(nodes_to_test, polygon_nodes, points):
    """
    Verilen düğümlerin verilen poligonun içinde olup olmadığını belirler.

    Args:
        nodes_to_test (np.ndarray): Poligonun içinde mi diye test edilecek noktaların indeksleri veya koordinatları
        polygon_nodes (np.ndarray): Poligonun points dizisindeki düğüm indeksleri
        points (np.ndarray): Tüm düğümlerin koordinatları — shape: (N, 2)

    Returns:
        np.ndarray: Boole dizisi — her bir node için True (içeride) veya False (dışarıda)

    Requires:
        shapely.geometry
        numpy
    """
    polygon_coords = points[polygon_nodes]
    polygon = shp.Polygon(polygon_coords)

    # Eğer düğüm noktalarının indeksleri verildi ise koordinatlarını bul,
    # Doğrudan koordinatları verildi ise onları kullan
    if nodes_to_test.ndim == 1: test_points = points[nodes_to_test]
    else                      : test_points = nodes_to_test
    
    return np.array([polygon.contains(shp.Point(p)) for p in test_points])