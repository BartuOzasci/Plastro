import numpy as np
"""
Required by:
    is_line_parallel_to_span
    is_line_within_distance
    project_line_onto_span
    find_wall_projections
    arrange_wall_projections
    refine_wall_projections
    merge_wall_lines
    build_data_span_walls
"""





def is_line_parallel_to_span(line, span_unit, cos_tol):
    """
    Verilen çizginin, yönü (birim vektörü) verilen aks parçasına, izin verilen açının
    kosinüsü cinsinden verilen bir toleransla paralel olup olmadığını kontrol eder.

    Args:
        line (np.ndarray)      : Çizgi başlangıç ve bitiş noktaları, [p1, p2] şeklinde
        span_unit (np.ndarray) : Aks parçasının yönü (birim vektörü)
        cos_tol (float)        : Paralellik toleransı, açının kosinüsü cinsinden

    Returns:
        bool: Eğer çizgi aks parçasına paralel ise True, aksi halde False
    
    Requires:
        numpy
    """
    line_vec = line[1] - line[0]
    line_vec_norm = np.linalg.norm(line_vec)
    
    # çizgi uzunluğu sıfırsa paralellik yok
    if line_vec_norm == 0: return False
    
    line_unit = line_vec / line_vec_norm
    cos_angle = abs(np.dot(line_unit, span_unit))
    
    return cos_angle >= cos_tol





def is_line_within_distance(line, span_start, span_unit, dProbe):
    """
    Verilen bir çizginin, span_start ile başlangıç noktası ve span_unit ile yönü verilen
    bir aks parçasına olan mesafesi, dProbe değerinden büyük değilse True döner.

    Args:
        line (np.ndarray)       : Çizgi başlangıç ve bitiş noktaları, [p1, p2] şeklinde
        span_start (np.ndarray) : Aks parçasının başlangıç noktası
        span_unit (np.ndarray)  : Aks parçasının yönü (birim vektörü)
        dProbe (float)          : Duvar çizgilerinin tespiti için mesafe toleransı

    Returns:
        bool: Eğer mesafe dProbe'dan büyük değilse True, aksi halde False
    
    Requires:
        numpy
    """
    for P in line:
        proj_len = np.dot(P - span_start, span_unit)
        foot     = span_start + proj_len * span_unit
        dist     = np.linalg.norm(P - foot)
        if dist > dProbe: return False
    return True





def project_line_onto_span(line, span_start, span_unit, span_len):
    """
    Verilen bir çizginin, span_start ile başlangıç noktası, span_unit ile yönü (birim vektörü)
    ve span_len ile uzunluğu verilen aks parçası üzerindeki izdüşümünün bağıl koordinatlarını ve
    aks parçasına olan dik ortalama mesafesini döndürür.
    
    Args:
        line (np.ndarray)       : Çizgi başlangıç ve bitiş noktaları, [p1, p2] şeklinde
        span_start (np.ndarray) : Aks parçasının başlangıç noktası
        span_unit (np.ndarray)  : Aks parçasının yönü (birim vektörü)
        span_len (float)        : Aks parçasının uzunluğu
    
    Returns:
        tuple: [t_min, t_max] şeklinde bağıl koordinatlar ve
               aks parçasına olan dik ortalama mesafe (signed distance)
    
    Requires:
        numpy    
    """
    # Projeksiyon aralığı
    p1, p2 = line
    t1 = np.dot(p1 - span_start, span_unit) / span_len
    t2 = np.dot(p2 - span_start, span_unit) / span_len
    t_min, t_max = sorted([t1, t2])

    # span'den taşan parçaları kırp
    t_min = max(0, min(1, t_min))
    t_max = max(0, min(1, t_max))
    # Eğer t_min < t_max değilse, çizginin span üzerinde bir izdüşümü yoktur.
    if not t_min < t_max: return False, False

    # span'a dik ortalama mesafe
    span_normal = np.array([-span_unit[1], span_unit[0]])
    mid = (p1 + p2) / 2
    vec_to_mid = mid - span_start
    signed_dist = np.dot(vec_to_mid, span_normal)

    return [t_min, t_max], signed_dist





def find_wall_projections(spans, nodes, wallLines, dProbe=30, tol_deg=1):
    """
    spans listesi ile verilmiş aks parçalarının üzerinde, wallLines ile verilen duvar çizgilerinin
    projeksiyonlarını ve ilgili çizgilerin işaretli (+ veya -) mesafelerini bulur.

    Args:
        spans (list)       : Aks parçalarının başlangıç ve bitiş düğüm indeksleri
        nodes (np.ndarray) : Düğümlerin koordinatlarını içeren (N, 2) numpy dizisi
        wallLines (list)   : Duvar çizgilerini temsil eden (M, 2, 2) numpy dizileri
        tol_deg (float)    : Açı toleransı (derece cinsinden)
        dProbe (float)     : Duvar çizgilerinin tespiti için mesafe toleransı

    Returns:
        matched_lines_list    : Her span için eşleşen t aralıkları
        signed_distances_list : Her span için işaretli (+ veya -) mesafeler
    
    Requires:
        numpy
    """
    cos_tol = np.cos(np.deg2rad(tol_deg))
    matched_lines_list, signed_distances_list = [], []
    wall_used_mask = np.zeros(len(wallLines), dtype=bool)

    for span in spans:
        A, B      = nodes[span[0]], nodes[span[1]]
        span_vec  = B - A
        span_len  = np.linalg.norm(span_vec)
        span_unit = span_vec / span_len

        matched_lines, signed_distances = [], []

        for i, line in enumerate(wallLines):
            if wall_used_mask[i]                                       : continue
            if not is_line_parallel_to_span(line, span_unit, cos_tol)  : continue
            if not is_line_within_distance(line, A, span_unit, dProbe) : continue

            t_range, signed_dist = project_line_onto_span(line, A, span_unit, span_len)
            
            if signed_dist is not False:
                matched_lines.append(t_range)
                signed_distances.append(signed_dist)
                wall_used_mask[i] = True  # çizgi artık kullanıldı
        
        matched_lines_list.append(np.array(matched_lines))
        signed_distances_list.append(np.array(signed_distances))

    return matched_lines_list, signed_distances_list





def arrange_wall_projections(matched_lines_list, signed_distances_list, tRound=3):
    """
    Her aks parçası (span) için hangi bağıl koordinatlar arasında, aks parçasına ne kadar
    (ORTALAMA) mesafede, hangi (EN BÜYÜK) kalınlıkta duvar parçaları olduğunu döndürür.

    Args:
        matched_lines_list    : Her span için eşleşen t aralıkları
        signed_distances_list : Her span için işaretli (+ veya -) mesafeler

    Returns:
        arranged_walls_list     : Her span üzerinde bulunan duvarların bağıl koordinatları
        arranged_distances_list : Her span üzerinde bulunan duvarların span eksenine olan işaretli
                                  (+ veya -) mesafeleri
        wall_widths_list        : Her span için duvar kalınlıkları
    
    Requires:
        numpy
    """
    arranged_walls_list, arranged_distances_list, wall_widths_list = [], [], []

    for matched_lines, signed_distances in zip(matched_lines_list, signed_distances_list):
        # Bu span için eşleşen duvar çizgisi yok. Tüm değerler -1 olarak ayarlanır.
        if len(matched_lines) == 0:
            arranged_walls_list.append(-1)
            arranged_distances_list.append(-1)
            wall_widths_list.append(-1)
            continue

        # 1. Uç noktaları topla
        all_points = set()
        for t1, t2 in matched_lines:
            all_points.add(round(t1, tRound))
            all_points.add(round(t2, tRound))
        points = sorted(all_points)

        # 2. Aralıkları oluştur
        arranged_wall_lines = []
        for i in range(len(points) - 1):
            a, b = points[i], points[i + 1]
            if b > a: arranged_wall_lines.append([a, b])

        # 3. Her aralığın kapsandığı çizgilerin signed mesafelerine bak
        arranged_distances, wall_widths = [], []
        for a, b in arranged_wall_lines:
            found_distances = []
            for (t1, t2), d in zip(matched_lines, signed_distances):
                if t1 <= a and b <= t2: found_distances.append(d)
            
            # Eğer ilgili aralıkta 2'den az çizgi varsa, o aralıkta duvar
            # yoktur. Duvar mesafesini ve genişliğini 0 olarak ayarla
            if len(found_distances) < 2:
                arranged_distances.append(0)
                wall_widths.append(0)
            # Eğer ilgili aralıkta 2 veya daha fazla çizgi varsa, o aralıkta
            # duvar vardır. Mesafeyi ve genişliği hesapla
            else:
                dMin, dMax = min(found_distances), max(found_distances)
                arranged_distances.append((dMin + dMax)/2)
                wall_widths.append(dMax - dMin)

        arranged_walls_list.append(np.array(arranged_wall_lines))
        arranged_distances_list.append(np.array(arranged_distances))
        wall_widths_list.append(np.array(wall_widths))

    return arranged_walls_list, arranged_distances_list, wall_widths_list





def refine_wall_projections(arranged_walls_list, arranged_distances_list, wall_widths_list):
    """
    Her aks parçası (span) için verilen duvar çizgisi, mesafesi ve (varsa) genişliği bilgilerini
    rafine eder. Bu işi, duvar oluşturmayan duvar çizgilerini kaldırarak yapar.
    
    Args:
        arranged_walls_list     : Her aks parçası (span) üzerinde bulunan duvar çizgilerinin bağıl koordinatları
        arranged_distances_list : Her aks parçası (span) üzerinde bulunan duvar çizgilerinin span eksenine olan
                                  işaretli (+ veya -) mesafeleri
        wall_widths_list        : Her aks parçası (span) üzerinde bulunan duvar çizgileri analiz edilerek çıkarılan
                                  duvar kalınlıkları
    
    Returns:
        refined_walls_list       : Her aks parçası (span) üzerinde bulunan rafine edilmiş duvar çizgilerinin bağıl
                                   koordinatları
        refined_distances_list   : Her aks parçası (span) üzerinde bulunan rafine edilmiş duvar çizgilerinin span
                                   eksenine olan işaretli (+ veya -) mesafeleri
        refined_wall_widths_list : Her aks parçası (span) için rafine edilmiş duvarlar kalınlıkları

    Requires:
        numpy  
    """
    refined_walls_list, refined_distances_list, refined_wall_widths_list = [], [], []
    
    for walls, distances, widths in zip(arranged_walls_list, arranged_distances_list, wall_widths_list):
        
        if isinstance(widths, int) and widths == -1:
            # Eğer ilgili aks aralığında hiç DUVAR ÇİZGİSİ yoksa, tüm değerleri -1 olarak ayarla
            refined_walls_list.append(-1)
            refined_distances_list.append(-1)
            refined_wall_widths_list.append(-1)
            continue
        
        refined_walls, refined_distances, refined_wall_widths = [], [], []
        
        for wall, distance, width in zip(walls, distances, widths):
            if not width == 0:
                # Eger mesafe 0 degilse, araligi ve mesafeyi ekle
                refined_walls.append(wall)
                refined_distances.append(distance)
                refined_wall_widths.append(width)

        # Eger ilgili aks aralığında hiç DUVAR yoksa, tüm değerleri -1 olarak ayarla
        if len(refined_wall_widths) == 0:
            refined_walls_list.append(-1)
            refined_distances_list.append(-1)
            refined_wall_widths_list.append(-1)
        else:
            refined_walls_list.append(np.array(refined_walls))
            refined_distances_list.append(np.array(refined_distances))
            refined_wall_widths_list.append(np.array(refined_wall_widths))

    return refined_walls_list, refined_distances_list, refined_wall_widths_list





def merge_wall_lines(refined_walls_list, tol=1e-3):
    """
    Birbiri ile bağlantılı olan duvar çizgilerini birleştirir.

    Args:
        refined_walls_list : Her aks parçası (span) üzerinde bulunan rafine edilmiş duvar çizgilerinin
                             bağıl koordinatları
        tol (float)        : Bağlantı toleransı; iki bağıl nokta arasındaki mesafe bu değerden küçükse
                             bağlantı varlığı kabul edilir.
    
    Returns:
        merged_wall_lines  : Her aks parçası (span) için birleştirilmiş duvar çizgilerinin bağıl koordinatları
    
    Requires:
        numpy
    """
    merged_wall_lines = []

    for walls in refined_walls_list:
        if isinstance(walls, int) and walls == -1:
            merged_wall_lines.append(-1)
            continue

        merged_segments = []
        current_start, current_end = walls[0]

        for start, end in walls[1:]:
            if np.isclose(start, current_end, atol=tol):
                # Bağlantı devam ediyor
                current_end = end
            else:
                # Bağlantı kopuyor, önceki segmenti kaydet
                merged_segments.append(np.array([current_start, current_end]))
                current_start, current_end = start, end

        # Son segmenti ekle
        merged_segments.append(np.array([current_start, current_end]))
        # İlgili aks parçası (span) için birleştirilmiş segmentleri listeye ekle
        merged_wall_lines.append(merged_segments)

    return merged_wall_lines





def build_data_span_walls(spans, nodes, wallLines, dProbe=30):
    """
    Her aks parçasının üzerinde bulunan duvarlara ait özet bilgileri oluşturur.

    Args:
        spans (np.ndarray)     : Aks parçalarının başlangıç ve bitiş düğüm indeksleri
        nodes (np.ndarray)     : Düğümlerin koordinatlarını içeren (N, 2) numpy dizisi
        wallLines (np.ndarray) : Duvar çizgilerini temsil eden (M, 2, 2) numpy dizileri
        dProbe (float)         : Duvar çizgilerinin tespiti için mesafe toleransı
    
    Returns:
        walls_summary          : Her aks parçası için kesintisiz duvar parçalarının bağıl koordinatları
        wall_distances_summary : Her aks parçası için duvarların ortalama mesafelerinin işaretli (+ veya -)
                                 değerleri
        wall_widths_summary    : Her aks parçası için duvarların en büyük kalınlıklarının değerleri
        bileşenlerinden oluşan bir sözlük
    
    Requires:
        numpy
    """
    wall_lines, wall_distances = find_wall_projections(spans, nodes, wallLines, dProbe)
    wall_lines, wall_distances, wall_widths = arrange_wall_projections(wall_lines, wall_distances)
    wall_lines, wall_distances, wall_widths = refine_wall_projections(wall_lines, wall_distances, wall_widths)
    merged_wall_lines = merge_wall_lines(wall_lines)

    walls_summary, wall_distances_summary, wall_widths_summary = [], [], []

    for walls, dists, widths in zip(merged_wall_lines, wall_distances, wall_widths):
        if isinstance(walls, int) and walls == -1:
            walls_summary.append(-1)
            wall_distances_summary.append(-1)
            wall_widths_summary.append(-1)
            continue
        
        """
        Her aks parçasının [t1 ve t2 şeklinde]:
            1. Başlangıç bağıl koordinatından (0), hangi (t1) bağıl koordinatına kadar
            2. Hangi (t2) bağıl koordinatından, bitiş bağıl koordinatına (1) kadar
        kesintisiz duvar parçası olduğu belirlenir.
        
        [0,1] ise, hem başlangıç noktasından başlayan, hem de bitiş noktasında biten
        kesintisiz duvar parçaları yoktur.
        """
        w_summary = np.array([0,1])
        if walls[0][0]  == 0 : w_summary[0] = walls[0][1]
        if walls[-1][1] == 1 : w_summary[1] = walls[-1][0]

        """
        Her aks parçasının üzerinde bulunan duvarların ortalama mesafesi ve
        en büyük kalınlığı belirlenir.
        """
        dists_summary  = np.mean(dists)
        widths_summary = max(widths)

        """
        Aşağıdaki maddeler bir aks parçası için özet duvar bilgisini oluşturur.
            1. Kesintisiz duvar parçaları bilgisi
            2. Ortalama mesafe bilgisi
            3. En büyük duvar kalınlığı bilgisi
        """
        walls_summary.append(w_summary)
        wall_distances_summary.append(dists_summary)
        wall_widths_summary.append(widths_summary)

    return {
        "walls"     : walls_summary,
        "distances" : wall_distances_summary,
        "widths"    : wall_widths_summary
    }