import build_data_geo as buildGeo
"""
Required by:
    build_mask_col_outside_basePol
    build_mask_colSpan_outside_basePol
"""

import numpy as np
"""
Required by:
    build_mask_col_outside_basePol
    build_mask_col_inside_banned_area
    build_mask_col_basePol_corner
    build_mask_beam_inside_banned_area
    build_mask_beam_under_wall
    build_mask_colSpan_outside_basePol
    build_mask_colSpan_inside_banned_area
    build_mask_colSpan_short_or_long
    build_mask_outer
    build_mask_user
    combine_masks
"""

import func_geo_basic as geoBasic
"""
Required by:
    build_mask_outer
    build_mask_user
"""

import func_misc as misc
"""
Required by:
    apply_repair
"""





def build_mask_col_outside_basePol(nodes, axNod, basePol):
    """
    nodes listesinde verilen hangi düğümler üzerindeki noktasal kolonların basePol
    poligonunun dışında kaldığını belirler ve bir maske olarak döndürür. True, noktasal
    kolonun basePol poligonunun dışında kaldığını gösterir.

    Args:
        nodes (numpy.ndarray)     : Düğümlerin koordinatlarını içeren numpy dizisi
        axNod (list of np.arrays) : Eksenler üzerindeki düğümlerin indeksleri
        basePol (numpy.array)     : Oturma alanı poligonunun köşe koordinatlarının indeksleri

    Returns:
        np.array of bool: Her noktasal kolon için True / False değerlerinden oluşan dizi

    Requires:
        build_data_geo as buildGeo
        numpy as np
    """
    nodes_on_basePol = buildGeo.build_areaOnNod(axNod, [basePol])
    # Hiçbir alanın ÜZERİNDE değilse ilgili düğüm için -1 yazılır.
    # Aksi halde ilgili alanların indekslerini tutan bir np.array yazılır.
    on_basePol       = buildGeo.build_nodOnArea(nodes_on_basePol, nodes)

    nodes_in_basePol = buildGeo.build_areaInNod([basePol], nodes, nodes_on_basePol)
    # Hiçbir alanın İÇİNDE değilse ilgili düğüm için -1 yazılır.
    # Aksi halde ilgili alanların indekslerini tutan bir np.array yazılır.
    in_basePol       = buildGeo.build_nodInArea(nodes, nodes_in_basePol)

    mask_col_outside_basePol = [False] * len(nodes)
    
    for i in range(len(nodes)):
        if isinstance(on_basePol[i], int) and isinstance(in_basePol[i], int):
            mask_col_outside_basePol[i] = True

    return np.array(mask_col_outside_basePol)





def build_mask_col_inside_banned_area(nodInArea, no_columns):
    """
    İçinde kolon bulunmasına izin verilmeyen alanların içinde bulunan noktasal kolonları belirler
    ve bir maske olarak döndürür. True, noktasal kolonun yasaklı alan içinde bulunduğunu gösterir.

    Args:
        nodInArea (list)      : Her düğüm için içinde bulunduğu alan bilgilerini içeren listedir.
                                Elemanlar -1 (alan içinde değil) veya np.array (alan indeksleri) olabilir.
        no_columns (np.array) : Hangi alanların içinde kolon bulunmasına izin verilmediği bilgisini tutan
                                numpy dizisidir. 1 ise izin verilmiyor, 0 ise izin veriliyor.

    Returns:
        np.array : Hangi noktasal kolonun sistemde bulunmasının yasak olduğu bilgisini içeren maskedir.
                   True = Yasak, False = Yasak değil.

    Requires:
        numpy as np
    """
    mask_col_inside_banned_area = []

    for node_areas in nodInArea:
        is_banned = False

        # Eğer düğüm herhangi bir alanın içinde bulunuyorsa
        # yani nodInArea[i] != -1
        if isinstance(node_areas, np.ndarray):
            for area_index in node_areas:
                if no_columns[area_index] == 1:
                    is_banned = True
                    break

        mask_col_inside_banned_area.append(is_banned)

    return np.array(mask_col_inside_banned_area)





def build_mask_col_basePol_corner(nodes, basePol):
    """
    Oturma alanının köşe kolonlarına ait maskeyi oluşturur. True, ilgili düğümde
    kolon olduğunu gösterir.

    Args:
        nodes (numpy.ndarray) : Düğümlerin koordinatlarını içeren numpy dizisi
        basePol (numpy.array) : Oturma alanı poligonunun köşe koordinatlarının indeksleri

    Returns:
        numpy.ndarray: Oturma alanının köşe kolonlarına ait maske

    Requires:
        numpy
    """
    mask_col_basePol_corner = np.zeros(len(nodes), dtype=bool)
    mask_col_basePol_corner[basePol] = True
    return mask_col_basePol_corner





def build_mask_beam_inside_banned_area(spanInArea, no_beams):
    """
    İçinde kiriş bulunmasına izin verilmeyen alanların içinde bulunan kirişleri belirler
    ve bir maske olarak döndürür. True, kirişin yasaklı alan içinde bulunduğunu gösterir.

    Args:
        spanInArea (list)   : Her açıklık için içinde bulunduğu alan bilgilerini içeren listedir.
                              Elemanlar -1 (alan içinde değil) veya np.array (alan indeksleri) olabilir.
        no_beams (np.array) : Hangi alanların içinde kiriş bulunmasına izin verilmediği bilgisini tutan
                              numpy dizisidir. 1 ise izin verilmiyor, 0 ise izin veriliyor.

    Returns:
        np.array : Hangi kirişin sistemde bulunmasının yasak olduğu bilgisini içeren maskedir.
                   True = Yasak, False = Yasak değil.

    Requires:
        numpy as np
    """
    mask_beam_inside_banned_area = []

    for span_areas in spanInArea:
        is_banned = False

        # Eğer açıklık herhangi bir alanın içinde bulunuyorsa
        # yani spanInArea[i] != -1
        if isinstance(span_areas, np.ndarray):
            for area_index in span_areas:
                if no_beams[area_index] == 1:
                    is_banned = True
                    break

        mask_beam_inside_banned_area.append(is_banned)

    return np.array(mask_beam_inside_banned_area)





def build_mask_beam_under_wall(wall_widths, full_wall_min_width):
    """
    Üzerinde tam ve yarım duvar bulunan açıklıklar için hangi açıklıkta kiriş bulunması
    gerektiğini gösteren maskeleri oluşturur.

    Args:
        wall_widths (list): Her bir açıklıkta bulunan duvar kalınlıklarını içeren liste
                            -1, ilgili açıklıkta duvar olmadığını,
                            > 0, ilgili açıklıktaki duvar kalınlığını ifade eder.
        full_wall_min_width (float): Tam duvar olarak kabul edilecek minimum kalınlık

    Returns:
        tuple: İki boolean numpy dizisinden oluşan bir tuple döndürür.
               Birincisi tam duvarlı açıklıklar için maske  (True = tam duvar var)
               İkincisi yarım duvarlı açıklıklar için maske (True = yarım duvar var)

    Requires:
        numpy as np
    """
    mask_beam_under_wall_full, mask_beam_under_wall_half = [], []

    for width in wall_widths:
        is_full_wall, is_half_wall = False, False

        # Duvarın varlığını kontrol et (kalınlık -1 değilse)
        if width > 0:
            # Tam duvar mı?
            if width >= full_wall_min_width : is_full_wall = True
            # Yarım duvar mı?
            else                            : is_half_wall = True

        mask_beam_under_wall_full.append(is_full_wall)
        mask_beam_under_wall_half.append(is_half_wall)

    return np.array(mask_beam_under_wall_full), np.array(mask_beam_under_wall_half)





def build_mask_colSpan_outside_basePol(nodes, axNod, spans, basePol):
    """
    spans listesinde verilen hangi aks parçaları üzerindeki çizgisel kolonların basePol
    poligonunun dışında kaldığını belirler ve bir maske olarak döndürür. True, çizgisel
    kolonun basePol poligonunun dışında kaldığını gösterir.

    Args:
        nodes (numpy.ndarray)     : Düğümlerin koordinatlarını içeren numpy dizisi
        axNod (list of np.arrays) : Eksenler üzerindeki düğümlerin indeksleri
        spans (numpy.ndarray)     : Aks parçalarının başlangıç ve bitiş düğümlerini içeren
                                    numpy dizisi
        basePol (numpy.array)     : Oturma alanı poligonunun köşe koordinatlarının indeksleri

    Returns:
        np.array of bool: Her çizgisel kolon için True / False değerlerinden oluşan dizi

    Requires:
        build_data_geo as buildGeo
        numpy as np
    """
    nodes_on_basePol = buildGeo.build_areaOnNod(axNod, [basePol]) #! build_mask_col_outside_basePol'de de yapılıyor. Olsun :)
    # Hiçbir alanın ÜZERİNDE değilse ilgili düğüm için -1 yazılır.
    # Aksi halde ilgili alanların indekslerini tutan bir np.array yazılır.
    on_basePol       = buildGeo.build_spanOnArea(nodes_on_basePol, spans)

    basePol_on_spans = buildGeo.build_areaOnSpan(on_basePol, [basePol])
    basePol_in_spans = buildGeo.build_areaInSpan([basePol], nodes, spans, basePol_on_spans)
    # Hiçbir alanın İÇİNDE değilse ilgili düğüm için -1 yazılır.
    # Aksi halde ilgili alanların indekslerini tutan bir np.array yazılır.
    in_basePol       = buildGeo.build_spanInArea(spans, basePol_in_spans)

    mask_colSpan_outside_basePol = [False] * len(spans)
    
    for i in range(len(spans)):
        if isinstance(on_basePol[i], int) and isinstance(in_basePol[i], int):
            mask_colSpan_outside_basePol[i] = True

    return np.array(mask_colSpan_outside_basePol)





def build_mask_colSpan_inside_banned_area(spanInArea, no_columns):
    """
    İçinde kolon bulunmasına izin verilmeyen alanların içinde bulunan çizgisel kolonları belirler
    ve bir maske olarak döndürür. True, çizgisel kolonun yasaklı alan içinde bulunduğunu gösterir.

    Args:
        spanInArea (list)     : Her açıklık için içinde bulunduğu alan bilgilerini içeren listedir.
                                Elemanlar -1 (alan içinde değil) veya np.array (alan indeksleri) olabilir.
        no_columns (np.array) : Hangi alanların içinde kolon bulunmasına izin verilmediği bilgisini tutan
                                numpy dizisidir. 1 ise izin verilmiyor, 0 ise izin veriliyor.

    Returns:
        np.array : Hangi çizgisel kolonun sistemde bulunmasının yasak olduğu bilgisini içeren maskedir.
                   True = Yasak, False = Yasak değil.

    Requires:
        numpy as np
    """
    mask_colSpan_inside_banned_area = []

    for span_areas in spanInArea:
        is_banned = False

        # Eğer açıklık herhangi bir alanın içinde bulunuyorsa
        # yani spanInArea[i] != -1
        if isinstance(span_areas, np.ndarray):
            for area_index in span_areas:
                if no_columns[area_index] == 1:
                    is_banned = True
                    break

        mask_colSpan_inside_banned_area.append(is_banned)

    return np.array(mask_colSpan_inside_banned_area)





def build_mask_colSpan_short_or_long(spanLen, colSpanLenMin, colSpanLenMax):
    """
    İzin verilenden daha kısa veya uzun açıklıklara yerleştirilmiş çizgisel kolonlar
    için bir maske oluşturur. True, ilgili çizgisel kolonun izin verilenden kısa veya
    uzun olduğunu gösterir.

    Args:
        spanLen (numpy.ndarray) : Her bir aks parçasının uzunluklarını içeren numpy dizisi
        colSpanLenMin (float)   : Çizgisel kolonlar için izin verilen en kısa açıklık
        colSpanLenMax (float)   : Çizgisel kolonlar için izin verilen en uzun açıklık

    Returns:
        numpy.ndarray: Kısa veya uzun açıklıklara yerleştirilmiş çizgisel kolonlar için maske

    Requires:
        numpy as np
    """
    mask_colSpan_short_or_long = np.zeros(len(spanLen), dtype=bool)
    mask_colSpan_short_or_long[spanLen < colSpanLenMin] = True
    mask_colSpan_short_or_long[spanLen > colSpanLenMax] = True
    return mask_colSpan_short_or_long





def build_mask_outer(nodes, axNod, spans, nodMat, basePol, floorPol):
    """
    Oturma alanı (basePol) ve kat alanı (floorPol) üzerindeki düğümler ve aks parçaları için
    maskeler oluşturur.

    Args:
        nodes (np.ndarray)        : Düğümlerin koordinatlarını içeren numpy dizisi
        axNod (list of np.arrays) : Eksenler üzerindeki düğümlerin indeksleri
        spans (np.ndarray)        : Aks parçalarının başlangıç ve bitiş düğümlerini
                                    içeren numpy dizisi
        nodMat (np.ndarray)       : Düğümler arasındaki aks parçasının indeksini tutan matris
        basePol (np.ndarray)      : Oturma alanının köşe noktalarını içeren numpy dizisi
        floorPol (np.ndarray)     : Kat alanının köşe noktalarını içeren numpy dizisi

    Returns:
        dict of np.arrays : Oturma ve kat alanları üzerindeki düğümler ve aks
                            parçaları için maskeler

    Requires:
        numpy as np
        func_geo_basic as geoBasic
    """
    # Boş maskeleri oluştur
    mask_basePol_nodes  = np.array([False] * len(nodes))
    mask_basePol_spans  = np.array([False] * len(spans))
    mask_floorPol_nodes = np.array([False] * len(nodes))
    mask_floorPol_spans = np.array([False] * len(spans))

    # Oturma alanı üzerindeki düğümleri ve aks parçalarını bul
    basePol_nodes = geoBasic.stations_multiple(axNod, basePol)
    basePol_span_nodes = np.stack([basePol_nodes[:-1], basePol_nodes[1:]], axis=1)
    row_indices, col_indices = basePol_span_nodes[:, 0], basePol_span_nodes[:, 1]
    basePol_spans = nodMat[row_indices, col_indices]

    # Kat alanı üstindeki düğümleri ve aks parçalarını bul
    floorPol_nodes = geoBasic.stations_multiple(axNod, floorPol)
    floorPol_span_nodes = np.stack([floorPol_nodes[:-1], floorPol_nodes[1:]], axis=1)
    row_indices, col_indices = floorPol_span_nodes[:, 0], floorPol_span_nodes[:, 1]
    floorPol_spans = nodMat[row_indices, col_indices]

    # Maskeleri güncelle
    mask_basePol_nodes[basePol_nodes]   = True
    mask_basePol_spans[basePol_spans]   = True
    mask_floorPol_nodes[floorPol_nodes] = True
    mask_floorPol_spans[floorPol_spans] = True

    # Maskeleri döndür
    return {
        "mask_basePol_nodes"  : mask_basePol_nodes,
        "mask_basePol_spans"  : mask_basePol_spans,
        "mask_floorPol_nodes" : mask_floorPol_nodes,
        "mask_floorPol_spans" : mask_floorPol_spans
    }





def build_mask_user(nodes, spans, dxf):
    """
    dxf dosyasında kullanıcı tarafından belirtilen kısılar için maskeleri oluşturur.

    Args:
        nodes (np.ndarray) : Düğümlerin koordinatlarını içeren numpy dizisi
        spans (np.ndarray) : Aks parçalarının başlangıç ve bitiş düğümlerini
                             içeren numpy dizisi        
        dxf (dict)         : read_DXF ile DXF dosyasından okunan plastro bileşenlerini içeren sözlük

    Returns:
        dict of np.arrays  : Kullanıcı tarafından belirtilen kısılar için maskeler sözlüğü

    Requires:
        numpy as np
        func_geo_basic as geoBasic
    """
    # Boş maskeleri oluştur
    mask_col_always_user     = np.array([False] * len(nodes))
    mask_col_never_user      = np.array([False] * len(nodes))
    mask_colSpan_always_user = np.array([False] * len(spans))
    mask_colSpan_never_user  = np.array([False] * len(spans))
    mask_beam_always_user    = np.array([False] * len(spans))
    mask_beam_never_user     = np.array([False] * len(spans))

    # Kullanıcı tarafından işaretlenen noktaların hangi düğümlerin veya
    # hangi aks parçalarının üzerinde olduğunu bul
    #col_always     = geoBasic.point_indexes(dxf["alwaysCol"], nodes)
    #col_never      = geoBasic.point_indexes(dxf["neverCol"], nodes)
    #colSpan_always = geoBasic.points_on_spans(dxf["alwaysColSpan"], nodes, spans)
    #colSpan_never  = geoBasic.points_on_spans(dxf["neverColSpan"], nodes, spans)
    #beam_always    = geoBasic.points_on_spans(dxf["alwaysBeam"], nodes, spans)
    #beam_never     = geoBasic.points_on_spans(dxf["neverBeam"], nodes, spans)
    # ⚙️ Bu layer’lar devre dışı bırakıldı, dolayısıyla boş diziler atıyoruz
    col_always, col_never = np.array([], dtype=int), np.array([], dtype=int)
    colSpan_always, colSpan_never = np.array([], dtype=int), np.array([], dtype=int)
    beam_always, beam_never = np.array([], dtype=int), np.array([], dtype=int)


    # Bir düğüm veya aks parçası üzerinde olmayan noktalara ait -1
    # elemanlarını sil
    col_always     = col_always[col_always != -1]
    col_never      = col_never[col_never != -1]
    colSpan_always = colSpan_always[colSpan_always != -1]
    colSpan_never  = colSpan_never[colSpan_never != -1]
    beam_always    = beam_always[beam_always != -1]
    beam_never     = beam_never[beam_never != -1]

    # Bulunan düğümlere veya aks parçalarına karşılık gelen maske elemanlarını
    # True yap
    mask_col_always_user[col_always] = True
    mask_col_never_user[col_never]  = True
    mask_colSpan_always_user[colSpan_always] = True
    mask_colSpan_never_user[colSpan_never]  = True
    mask_beam_always_user[beam_always] = True
    mask_beam_never_user[beam_never]  = True

    # Maskeleri döndür
    return {
        "mask_col_always_user"     : mask_col_always_user,
        "mask_col_never_user"      : mask_col_never_user,
        "mask_colSpan_always_user" : mask_colSpan_always_user,
        "mask_colSpan_never_user"  : mask_colSpan_never_user,
        "mask_beam_always_user"    : mask_beam_always_user,
        "mask_beam_never_user"     : mask_beam_never_user
    } #! read_DXF fonksiyonu neverColPart bilgisini de okuyor. Ama kısıtlara henüz dahil edilmedi :(





def combine_masks(masks):
    """
    masks listesinde verilen maskeleri aşağıdaki kural ile birleştirir:
    Eğer tüm maskelerin aynı indeksinde tüm değerler False ise False, aksi halde True.

    Args:
        masks (list): Aynı boyutta boolean NumPy dizilerinden oluşan bir liste.

    Returns:
        np.ndarray: Birleştirilmiş maske
    
    Requires:
        numpy as np
    """
    # Dizileri dikey olarak birleştirerek tek bir 2D dizi oluşturma
    stacked_masks = np.stack(masks)
    # Her sütunda (yani her indekste), en az bir True değeri olup olmadığını kontrol etme
    combined_mask = np.any(stacked_masks, axis=0)
    
    return combined_mask





def build_data_repair(geoData, slabProp, span_walls, xls, dxf):
    """
    masks listesinde verilen maskeleri aşağıdaki kural ile birleştirir:
    Eğer tüm maskelerin aynı indeksinde tüm değerler False ise False, aksi halde True.

    Args:
        geoData    : Sistemin temel geometrik verisi (build_data_geo)
        slabProp   : Döşeme özellikleri sözlüğü
                     {coords, class, no columns, no beams, no slab, importance}
        span_walls : build_data_span_walls ile oluşturulan açıklık-duvar ilişkisi sözlüğü
        xls        : read_XLS.read_XLS ile okunan ayarlar (xls) dosyası
        dxf        : read_DXF.read_DXF ile okunan çizim (dxf) dosyası

    Returns:
        dict: tasarım vektörü onarımı için kısıt maskeleri

    Requires:
        none
    """
    # noktasal kolon maskeleri
    mask_col_outside_basePol    = build_mask_col_outside_basePol(geoData["nodes"], geoData["axNod"], geoData["basePol"])
    mask_col_inside_banned_area = build_mask_col_inside_banned_area(geoData["nodInArea"], slabProp["no columns"])
    mask_col_basePol_corner     = build_mask_col_basePol_corner(geoData["nodes"], geoData["basePol"])

    # kiriş maskeleri
    mask_beam_inside_banned_area = build_mask_beam_inside_banned_area(geoData["spanInArea"], slabProp["no beams"])
    #! 12.5 cm'den daha ince duvar yarım duvardır.
    #! Belki ileride ilgili ayar XLS dosyasına dahil edilebilir.
    mask_beam_under_wall_full, mask_beam_under_wall_half = build_mask_beam_under_wall(span_walls["widths"], 12.5)

    # çizgisel kolon maskeleri
    mask_colSpan_outside_basePol    = build_mask_colSpan_outside_basePol(geoData["nodes"], geoData["axNod"], geoData["spans"], geoData["basePol"])
    mask_colSpan_inside_banned_area = build_mask_colSpan_inside_banned_area(geoData["spanInArea"], slabProp["no columns"])
    mask_colSpan_short_or_long      = build_mask_colSpan_short_or_long(geoData["spanLen"], xls["colSpanLenLim"]["min"], xls["colSpanLenLim"]["max"])

    # oturma ve kat alanı üzerindeki düğümler ve aks parçaları için maskeler
    mask_outer = build_mask_outer(geoData["nodes"], geoData["axNod"], geoData["spans"], geoData["nodMat"], geoData["basePol"], geoData["floorPol"])

    # kullanıcı tanımlı maskeler
    mask_user  = build_mask_user(geoData["nodes"], geoData["spans"], dxf)

    # maskeleri grupla
    mask_col_always = combine_masks([
        mask_col_basePol_corner, #! Bu şüpheli; çizgisel kolon durumlarında çakışma olabilir.
        mask_user["mask_col_always_user"]
    ])

    mask_col_never = combine_masks([
        mask_col_outside_basePol,
        mask_col_inside_banned_area,
        mask_user["mask_col_never_user"]
    ])

    mask_beam_always = combine_masks([
        mask_beam_under_wall_full,
        mask_beam_under_wall_half,
        mask_outer["mask_basePol_spans"],
        mask_outer["mask_floorPol_spans"],
        mask_user["mask_beam_always_user"]
    ])

    mask_beam_never = combine_masks([
        mask_beam_inside_banned_area,
        mask_user["mask_beam_never_user"]
    ])

    mask_colSpan_always = mask_user["mask_colSpan_always_user"]

    mask_colSpan_never = combine_masks([
        mask_colSpan_outside_basePol,
        mask_colSpan_inside_banned_area,
        mask_colSpan_short_or_long,
        mask_user["mask_colSpan_never_user"]
    ])

    # maskeleri döndür
    return {
        "mask_col_always"     : mask_col_always,
        "mask_col_never"      : mask_col_never,
        "mask_beam_always"    : mask_beam_always,
        "mask_beam_never"     : mask_beam_never,
        "mask_colSpan_always" : mask_colSpan_always,
        "mask_colSpan_never"  : mask_colSpan_never,
        "mask_basePol_nodes"  : mask_outer["mask_basePol_nodes"],
        "mask_basePol_spans"  : mask_outer["mask_basePol_spans"],
        "mask_floorPol_nodes" : mask_outer["mask_floorPol_nodes"],
        "mask_floorPol_spans" : mask_outer["mask_floorPol_spans"]
    }





def apply_repair(cand, repair_mask):
    """
    cand listesine (çözüm adayı) build_data_repair fonksiyonu ile elde edilen onarım maskelerini
    (repair_mask) uygular.

    Args:
        cand (list)        : Çözümün tasarım vektörü (manual_design_vector.md dosyasına bakınız)
        repair_mask (dict) : build_data_repair fonksiyonu ile elde edilen onarım maskeleri

    Returns:
        list: cand listesinin onarım maskeleri uygulanmış yeni bir kopyası
    
    Requires:
        func_misc as misc
    """
    mask_list = [
        repair_mask["mask_col_always"],
        repair_mask["mask_col_never"],
        repair_mask["mask_beam_always"],
        repair_mask["mask_beam_never"],
        repair_mask["mask_colSpan_always"],
        repair_mask["mask_colSpan_never"]
    ]
    
    # 2 x colTopo, 2 x beamTopo, 2 x colSpanTopo maskesi vardır.
    # bu sebeple idx_list aşağıdaki gibi olmalıdır.
    idx_list = [0, 0, 8, 8, 5, 5]

    option_list = [
        "True_is_1",
        "True_is_0",
        "True_is_1",
        "True_is_0",
        "True_is_1",
        "True_is_0"
    ]

    return misc.apply_masks(cand, idx_list, mask_list, option_list)