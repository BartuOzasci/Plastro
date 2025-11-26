import numpy as np
"""
Required by:
    build_draft_contBeam
    add_equivalent_contBeam_info
    add_close_contBeam_info
    add_end_allowed_col_info
    add_outer_contBeam_info
    add_never_contBeam_info
    add_fitness_info
    update_never_contBeam_info
    build_mask_contBeam_never
    update_equivalent_and_close_info
    add_include_exclude_info
"""

import copy
"""
Required by:
    add_equivalent_contBeam_info
    add_close_contBeam_info
    add_end_allowed_col_info
    add_outer_contBeam_info
    add_never_contBeam_info
    add_fitness_info
    update_never_contBeam_info
    update_equivalent_and_close_info
    add_include_exclude_info
"""





def build_draft_contBeam(axNod, axSpan, all_path_details):
    """
    Sisteme eklenebilecek tüm sürekli kiriş hatlarını taslak olarak oluşturur.

    Args:
        axNod (list of np.arrays): Eksenler üzerindeki düğümlerin indeksleri
        axSpan (list of np.arrays): Akslar üzerindeki düğümler arasındaki aks parçalarının
                                    indeksleri
        all_path_details: build_data_cont_lines.py modülü ile oluşturulan sürekli hat
                          detaylarının listesi

    Returns:
        list of dict of np.arrays: Sisteme eklenebilecek tüm sürekli kiriş hatlarının
                                   detaylarının listesi

    Requires:
        numpy as np
    """
    draft_contBeam = []

    for i in range(len(axNod)):
        draft_contBeam.append({
            "axes"    : np.array([i]),
            "nodes"   : axNod[i],
            "colSpan" : np.array([], dtype=int),
            "beam"    : axSpan[i]
        })
    
    for i, axis_i in enumerate(all_path_details):
        for j, axis_j in enumerate(axis_i):
            
            # Eğer i ile j aksları kullanılarak oluşturulabilecek sürekli hat yoksa
            # axis_j == -1 olur.
            if axis_j == -1: continue
            
            for cont_line in axis_j:
                draft_contBeam.append({
                    "axes"    : np.array([i,j]),
                    "nodes"   : cont_line["path"],
                    "colSpan" : cont_line["jump axis spans"],
                    "beam"    : cont_line["same axis spans"]
                })

    return draft_contBeam





def add_equivalent_contBeam_info(draft_contBeam):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş hatları taslağındaki
    her sürekli kiriş hattı için, birbirine denk (eşdeğer) sürekli kiriş hatlarının
    indekslerini "equivalent to" anahtarına ekler.

    Args:
        draft_contBeam : build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş
                         hatları taslağı

    Returns:
        list of dict of np.arrays : Eşdeğer sürekli kiriş hatlarının indekslerinin eklendiği
                                    sürekli kiriş hatları taslağı

    Requires:
        copy
        numpy as np
    """
    new_draft_contBeam = copy.deepcopy(draft_contBeam)
    axes_list = [set(i["axes"]) for i in new_draft_contBeam]

    for i, axes_i in enumerate(axes_list):
        equivalents = [] # boş eşdeğer sürekli kiriş hatları listesi
        
        for j, axes_j in enumerate(axes_list):
            if i != j and not axes_i.isdisjoint(axes_j):
                # ortak eleman varsa equivalents listesine ekle
                equivalents.append(j)
        
        # eğer eşdeğer sürekli kiriş hattı yoksa boş numpy dizisi yaz
        if len(equivalents) == 0:
            new_draft_contBeam[i]["equivalent to"] = np.array([], dtype=int)
        else:
            # varsa indekslerini numpy dizisi olarak yaz
            new_draft_contBeam[i]["equivalent to"] = np.array(equivalents, dtype=int)

    return new_draft_contBeam





def add_close_contBeam_info(draft_contBeam, spanDistMin, spanDistMinLim):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş hatları taslağındaki
    her sürekli kiriş hattı için yakın sürekli kiriş hatlarının indekslerini ekler.

    Args:
        draft_contBeam : build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş
                         hatları taslağı
        spanDistMin    : Kirişler arası minimum mesafeler matrisi (geoData["spanDistMin"])
        spanDistMinLim : Kirişler arası mesafe için izin verilen en küçük değer

    Returns:
        list of dict of np.arrays : Yakın sürekli kiriş hatlarının indekslerinin eklendiği
                                    sürekli kiriş hatları taslağı

    Requires:
        copy
        numpy as np
    """
    new_draft_contBeam = copy.deepcopy(draft_contBeam)
    
    for i in range(len(new_draft_contBeam)):
        for j in range(i+1, len(new_draft_contBeam)):
            
            beams_i, beams_j = new_draft_contBeam[i]["beam"], new_draft_contBeam[j]["beam"]
            
            # i ve j hatlarının birbirine en yakın kirişlerinin arasındaki mesafe
            span_dists = spanDistMin[beams_i][:, beams_j]
            span_dists = span_dists[span_dists != -1]
            
            # eğer iki hattın kirişleri arasında bir mesafeden söz edilemiyorsa
            if len(span_dists) == 0: continue

            # eğer iki hattın kirişleri arasındaki en kısa mesafe, izin verilen sınır değerden
            # küçük ise
            if min(span_dists) <= spanDistMinLim:
                # i hattının bilgisini güncelle
                if "close to" not in new_draft_contBeam[i]:
                    new_draft_contBeam[i]["close to"] = [j]
                else:
                    new_draft_contBeam[i]["close to"].append(j)
                # j hattının bilgisini güncelle
                if "close to" not in new_draft_contBeam[j]:
                    new_draft_contBeam[j]["close to"] = [i]
                else:
                    new_draft_contBeam[j]["close to"].append(i)
    
    # Hiçbir hatta "close to" bilgisi eklenmemiş olabilir. Bu durumda boş numpy dizisi yazılır.
    for i in range(len(new_draft_contBeam)):
        if "close to" not in new_draft_contBeam[i]:
            new_draft_contBeam[i]["close to"] = np.array([], dtype=int)
        else:
            new_draft_contBeam[i]["close to"] = np.array(new_draft_contBeam[i]["close to"])
    
    return new_draft_contBeam





def add_end_allowed_col_info(draft_contBeam, mask_col_never):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş hatları taslağına,
    her sürekli kiriş hattı için, yasak olmayan en uç noktasal kolonlara ait düğümlerin
    indekslerini ve "uç kolon skoru"nu ekler. Bir sürekli hattın uç kolonları, hattın
    başlangıç ve bitiş düğümlerine ne kadar yakınsa skor o kadar yüksek olur.

    Args:
        draft_contBeam : build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş
                         hatları taslağı
        mask_col_never : build_data_repair fonksiyonu ile oluşturulan yasak
                         (izin verilmeyen) noktasal kolonlar için maske

    Returns:
        list of dict of np.arrays: İzin verilen uç düğümlerin indekslerinin ve "uç kolon
                                   skoru"nun eklendiği sürekli kiriş hatları taslağı

    Requires:
        copy
        numpy as np
    """
    mask_col_allowed   = ~mask_col_never
    new_draft_contBeam = copy.deepcopy(draft_contBeam)

    for i, one_cont_beam in enumerate(new_draft_contBeam):
        # izin verilen düğümler (kolonlar)
        nodes_allowed = mask_col_allowed[one_cont_beam["nodes"]]
        
        if not any(nodes_allowed):
            # Eğer sürekli kiriş hattındaki hiçbir düğüme (kolona) izin
            # verilmiyorsa boş numpy dizisi yazılır.
            new_draft_contBeam[i]["end col"] = np.array([], dtype=int)
            # doğal olarak uç kolon skoru da 0 olur
            new_draft_contBeam[i]["end col score"] = 0
        else:
            # Sürekli kiriş hattındaki en az bir düğüme (kolona) izin veriliyorsa
            # ilk ve son düğümün (kolonun) indeksleri yazılır.
            first_idx  = np.argmax(nodes_allowed)
            first_node = one_cont_beam["nodes"][first_idx]

            last_idx   = len(one_cont_beam["nodes"]) - 1 - np.argmax(nodes_allowed[::-1])
            last_node  = one_cont_beam["nodes"][last_idx]

            # uç kolonların düğüm indeksleri
            new_draft_contBeam[i]["end col"] = np.array([first_node, last_node])
            
            # uç kolon skoru
            max_idx = len(one_cont_beam["nodes"]) - 1
            new_draft_contBeam[i]["end col score"] = (max_idx + last_idx - first_idx) / (2 * max_idx)

    return new_draft_contBeam





def add_outer_contBeam_info(draft_contBeam, mask_basePol_spans):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş hatları taslağına,
    her sürekli kiriş hattı için, dış (çevre) hat olup olmadığı bilgisini ekler. 

    Args:
        draft_contBeam     : build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş
                             hatları taslağı
        mask_basePol_spans : build_data_repair fonksiyonu ile oluşturulan dış (çevre)
                             kirişler için maske

    Returns:
        list of dict of np.arrays : Dış (çevre) hat bilgisini de bulunduran sürekli kiriş
                                    hatları taslağı

    Requires:
        copy
        numpy as np
    """
    new_draft_contBeam = copy.deepcopy(draft_contBeam)
    
    for i in new_draft_contBeam:
        # i. sürekli hatta ait kirişlerin "dış kiriş" olup olmama durumları
        mask_values = mask_basePol_spans[i["beam"]]
        # kaç tanesi "dış kiriş" ?
        true_count = np.count_nonzero(mask_values)
        # Eğer en az yarısı "dış kiriş" ise True
        i["outer"] = true_count >= (len(i["beam"]) / 2)

    return new_draft_contBeam





def add_never_contBeam_info(draft_contBeam, mask_beam_never, mask_colSpan_never):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş hatları taslağına,
    her sürekli kiriş hattı için, yasak olup olmadığı bilgisini ekler. 

    Args:
        draft_contBeam     : build_draft_contBeam fonksiyonu ile oluşturulan sürekli
                             kiriş hatları taslağı
        mask_beam_never    : build_data_repair fonksiyonu ile oluşturulan yasak
                             kirişler için maske
        mask_colSpan_never : build_data_repair fonksiyonu ile oluşturulan yasak
                             çizgisel kolonlar için maske

    Returns:
        list of dict of np.arrays : Yasak hat bilgisini de bulunduran sürekli kiriş
                                    hatları taslağı

    Requires:
        copy
        numpy as np
    """
    new_draft_contBeam = copy.deepcopy(draft_contBeam)
    
    for item in new_draft_contBeam:
        # yasak kiriş içerip içermediğinin kontrolü
        beam_banned = np.any(mask_beam_never[item["beam"]])
        # yasak çizgisel kolon içerip içermediğinin kontrolü
        colSpan_banned = np.any(mask_colSpan_never[item["colSpan"]])
        # herhangi biri yasak eleman içeriyorsa -> banned = True
        item["banned"] = bool(beam_banned or colSpan_banned)

    return new_draft_contBeam





def add_fitness_info(draft_contBeam, fitness_span_in_area):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan sürekli kiriş hatları taslağına,
    her sürekli kiriş hattı için, kirişler ve çizgisel kolonlar özelinde uygunluk (fitness)
    bilgisini ekler.

    Args:
        draft_contBeam       : build_draft_contBeam fonksiyonu ile oluşturulan sürekli
                               kiriş hatları taslağı
        fitness_span_in_area : build_fitness_span_in_area fonksiyonu ile oluşturulan,
                               açıklıkların uygunluk (fitness) değerleri dizisi

    Returns:
        list of dict of np.arrays : kiriş ve çizgisel kolon uygunluk (fitness) bilgisini de
                                    bulunduran sürekli kiriş hatları taslağı

    Requires:
        copy
        numpy as np
    """
    new_draft_contBeam = copy.deepcopy(draft_contBeam)

    # her sürekli kiriş hattı için fitness değeri hesapla ve ekle
    for cont in new_draft_contBeam:
        members         = np.concatenate([cont["beam"], cont["colSpan"]])
        cont["fitness"] = np.sum(fitness_span_in_area[members])
    
    # fitness değerlerini ayrı bir dizide topla
    fitness_values = np.array([cont["fitness"] for cont in new_draft_contBeam])
    max_fit_val    = np.max(fitness_values)
    
    # fitness değerlerini normalize et
    if max_fit_val == 0 : norm_fit_values = np.zeros_like(fitness_values)
    else                : norm_fit_values = fitness_values / max_fit_val
    
    # normalize edilmiş fitness değerlerini sürekli kiriş hatlarına ekle
    for cont, norm in zip(new_draft_contBeam, norm_fit_values):
        cont["fitness"] = norm

    return new_draft_contBeam





def update_never_contBeam_info(draft_contBeam):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan taslak sürekli kiriş hatlarının
    yasak olup olmadıklarına ilişkin bilgiyi aşağıdaki işlemler ile günceller. Bir
    grup denk sürekli hat içerisinde en iyi olan hariç diğerlerinin seçenekler içinde
    bulunması anlamsızdır. Her bir sürekli hat için:
    - Eğer sürekli hat zaten ziyaret edilmiş ise atla
    - Eğer sürekli hat yasaklı ise atla
    - Kendisi ve "equivalent to" ile belirtilen (ve yasak olmayan) sürekli hatlardan
      oluşan grubu oluştur
    - Grup içinde eğer dış hat (outer) varsa, sadece dış hatları değerlendir; yoksa
      tüm hatları değerlendir
    - Önce "end col score" değeri en büyük olan(lar) seçilir
    - Sonra fitness en küçük olan(lar) seçilir
    - Grup içindeki sürekli hatlardan sadece seçilenler (winners) tutulur, diğerleri
      yasaklanır

    Args:
        draft_contBeam : build_draft_contBeam fonksiyonu ile oluşturulup, gerekli
                         anahtarları eklenmiş sürekli kiriş hatları taslağı

    Returns:
        list of dict of np.arrays : "banned" anahtarı güncellenmiş sürekli kiriş
                                    hatlarının listesi

    Requires:
        copy
        numpy as np
    """
    new_contBeam = copy.deepcopy(draft_contBeam)
    visited      = np.zeros(len(new_contBeam), dtype=bool)

    for i, cont in enumerate(new_contBeam):
        # Zaten ziyaret edilmiş veya yasaklı ise atla
        if visited[i] or cont["banned"]: continue

        # Yasaklı olmayan denk hatlardan grup oluştur (kendisi + equivalent to)
        eq_indices = [idx for idx in cont["equivalent to"] if not new_contBeam[idx]["banned"]]
        group_indices = [i] + eq_indices
        
        # Ziyaret edilmiş olarak işaretle
        for idx in group_indices: visited[idx] = True

        # Grup içindeki sürekli hatları ve gerekli anahtarlarını al
        group        = [new_contBeam[idx] for idx in group_indices]
        fitness_vals = np.array([g["fitness"] for g in group])
        outer_flags  = np.array([g["outer"] for g in group])
        endcol_vals  = np.array([g["end col score"] for g in group])

        # Eğer grup içinde dış hat varsa, sadece dış hatları değerlendir
        if np.any(outer_flags) : mask = outer_flags
        else                   : mask = np.ones(len(group), dtype=bool)

        # Önce "end col score" değeri en büyük olan(lar)
        max_endcol      = np.max(endcol_vals[mask])
        mask_max_endcol = mask & (endcol_vals == max_endcol)

        # Sonra fitness değeri en küçük olan(lar)
        min_fit = np.min(fitness_vals[mask_max_endcol])
        winners = mask_max_endcol & (fitness_vals == min_fit)

        # ilgili hatların "banned" anahtarlarını güncelle
        for idx, keep in zip(group_indices, winners):
            new_contBeam[idx]["banned"] = not keep

    return new_contBeam





def update_equivalent_and_close_info(draft_contBeam):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan taslak sürekli kiriş hatlarının
    denk ve yakın hat bilgilerini, yasaklı hat bilgisine göre günceller. Denk ve yakın
    hat listelerinde yasaklı hatların bulunması anlamsızdır.

    Args:
        draft_contBeam : build_draft_contBeam fonksiyonu ile oluşturulup, "banned"
                         anahtarı güncellenmiş sürekli kiriş hatları taslağı

    Returns:
        list of dict of np.arrays : "close to" ve "equivalent to" anahtarları
                                    güncellenmiş sürekli kiriş hatlarının listesi

    Requires:
        copy
        numpy as np
    """
    new_contBeam = copy.deepcopy(draft_contBeam)

    for cont in new_contBeam:
        # "close to" anahtarını güncelle
        if cont["close to"].size > 0:  # boş değilse
            mask = [not new_contBeam[idx]["banned"] for idx in cont["close to"]]
            cont["close to"] = cont["close to"][mask] if np.any(mask) else np.array([], dtype=int)

        # "equivalent to" anahtarını güncelle
        if cont["equivalent to"].size > 0:  # boş değilse
            mask = [not new_contBeam[idx]["banned"] for idx in cont["equivalent to"]]
            cont["equivalent to"] = cont["equivalent to"][mask] if np.any(mask) else np.array([], dtype=int)

    return new_contBeam





def add_include_exclude_info(draft_contBeam):
    """
    build_draft_contBeam fonksiyonu ile oluşturulan taslak sürekli kiriş hatlarına,
    "include" ve "exclude" anahtarlarını ekler. "include" anahtarı, ilgili sürekli kiriş
    hattının sistemde bulunması durumunda sisteme dahil edilmesi gereken sürekli kiriş
    hatlarının indekslerini içerir. "exclude" anahtarı ise, ilgili sürekli kiriş hattının
    sistemde bulunması durumunda sistemden çıkarılması gereken sürekli kiriş hatlarının
    indekslerini içerir. Aşağıdaki kurallar uygulanır:
    1. Eğer sürekli kiriş hattının "outer" anahtarı True ise:
        - "include" anahtarı boş dizidir.
        - "exclude" anahtarı, "equivalent to" ve "close to" anahtarlarının birleşiminden oluşur.
    2. Eğer sürekli kiriş hattının "outer" anahtarı False ise:
        a. Eğer "close to" anahtarındaki dizide verilen sürekli kiriş hatlarının hepsinin "outer"
           anahtarı False ise:
            - "include" anahtarı boş dizidir.
            - "exclude" anahtarı, "equivalent to" ve "close to" anahtarlarının birleşiminden oluşur.
        b. Eğer "close to" anahtarındaki dizide verilen sürekli kiriş hatlarından en az birinin
           "outer" anahtarı True ise (bu hat A hattı olarak adlandırılsın):
            - "include" anahtarı np.array([A]) şeklinde tek elemanlı bir dizi olmalıdır.
            - "exclude" anahtarı, mevcut sürekli hattın indeksi, "equivalent to" ve "close to"
              anahtarlarının birleşiminden oluşur, ancak A hattı bu birleşimden çıkarılır.

    Args:
        draft_contBeam : build_draft_contBeam fonksiyonu ile oluşturulmuş sürekli kiriş hatları
                         taslağı

    Returns:
        list of dict of np.arrays : "include" ve "exclude" anahtarları eklenmiş sürekli kiriş
                                    hatları taslağı

    Requires:
        copy
        numpy as np
    """
    new_contBeam = copy.deepcopy(draft_contBeam)


    for idx, cont in enumerate(new_contBeam):
        eqv, close, outer = cont["equivalent to"], cont["close to"], cont["outer"]

        if outer:  # 1. "outer" = True
            include = np.array([], dtype=int)
            exclude = np.concatenate([eqv, close]) if (eqv.size + close.size) > 0 else np.array([], dtype=int)

        else:  # 2. "outer" = False
            if close.size == 0:
                include = np.array([], dtype=int)
                exclude = eqv.copy()
            else:
                close_outers = [c for c in close if new_contBeam[c]["outer"]]

                if len(close_outers) == 0:  # 2a. hepsi False
                    include = np.array([], dtype=int)
                    exclude = np.concatenate([eqv, close]) if (eqv.size + close.size) > 0 else np.array([], dtype=int)
                else:  # 2b. en az biri True
                    include = np.array([close_outers[0]], dtype=int)
                    exclude = np.setdiff1d(np.concatenate([[idx], eqv, close]), include)

        cont["include"] = include
        cont["exclude"] = exclude

    return new_contBeam





def build_contBeam(geoData, all_path_details, xls, repair_mask, fitness_span_in_area):
    """
    Sisteme eklenebilecek tüm sürekli kiriş hatlarını oluşturur ve bu hatları aşağıdaki
    bilgileri de içeren bir sözlükler listesi olarak döndürür.
    [
        {
            axes          : [0,1,...] - sürekli hattın elemanları hangi akslar üzerinde
            nodes         : [2,3,...] - sürekli hat sırasıyla hangi düğümleri takip ediyor
            colSpan       : [9,2,...] - sürekli hattaki çizgisel kolonların span numaraları
            beam          : [7,8,...] - sürekli hattaki kirişlerin span numaraları
            equivalent to : [5,9,...] - sürekli hat hangi diğer sürekli hatlara denk
            close to      : [3,6,...] - sürekli hat hangi diğer sürekli hatlara çok yakın
            end col       : [3,8]     - sürekli hattaki yasak olmayan uç kolonların numaraları
            end col score : float     - sürekli hattın "uç kolon skoru"
            outer         : bool      - sürekli hat dış (çevre) hat mı?
            banned        : bool      - sürekli hat yasaklı mı?
            fitness       : float     - sürekli hattın kiriş ve çizgisel kolon özelinde uygunluk
                                        (fitness) değeri
            include       : [4,7,...] - söz konusu sürekli hat sisteme eklenirse, sisteme dahil
                                        edilecek sürekli hatların indeksleri
            exclude       : [1,5,...] - söz konusu sürekli hat sisteme eklenirse, sistemden
                                        çıkarılacak sürekli hatların indeksleri
        }
        ,
        ...
    ]

    Args:
        geoData              : Sistemin temel geometrik verisi (build_data_geo)
        all_path_details     : build_data_cont_lines.py modülü ile oluşturulan sürekli hat
                               detaylarının listesi
        xls                  : read_XLS.read_XLS ile okunan ayarlar (xls) dosyası
        repair_mask          : build_data_repair fonksiyonu ile oluşturulan maskeler sözlüğü
        fitness_span_in_area : build_fitness_span_in_area fonksiyonu ile oluşturulan,
                               açıklıkların uygunluk (fitness) değerleri dizisi

    Returns:
        list of dict of np.arrays : Sisteme eklenebilecek tüm sürekli kiriş hatlarının listesi

    Requires:
        none
    """
    # sürekli kiriş hatları taslağını oluştur
    contBeam = build_draft_contBeam(geoData["axNod"], geoData["axSpan"], all_path_details)
    
    # denk hatlar bilgisini ekle
    contBeam = add_equivalent_contBeam_info(contBeam)
    # yakın hatlar bilgisini ekle
    contBeam = add_close_contBeam_info(contBeam, geoData["spanDistMin"], xls["beamDist"]["min"])
    
    # uç kolonlar ve uç kolon skoru bilgilerini ekle
    contBeam = add_end_allowed_col_info(contBeam, repair_mask["mask_col_never"])
    
    # dış (çevre) hat bilgisini ekle
    contBeam = add_outer_contBeam_info(contBeam, repair_mask["mask_basePol_spans"])
    # yasak hat bilgisini ekle
    contBeam = add_never_contBeam_info(contBeam, repair_mask["mask_beam_never"], repair_mask["mask_colSpan_never"])

    # kiriş ve çizgisel kolon uygunluk (fitness) bilgisini ekle
    contBeam = add_fitness_info(contBeam, fitness_span_in_area)

    # Yasaklı hatları güncelle
    contBeam = update_never_contBeam_info(contBeam)
    # Denk ve yakın hat bilgilerini güncelle
    contBeam = update_equivalent_and_close_info(contBeam)
    # Sisteme dahil edilecek ve sistemden çıkarılacak hat bilgilerini ekle
    contBeam = add_include_exclude_info(contBeam)

    return contBeam





# -----------------------------------------------------------------------------------------------------------------





def build_mask_contBeam_never(contBeam):
    """
    Yasaklı sürekli kiriş hatları için maske oluşturur.

    Args:
        contBeam : build_contBeam fonksiyonu ile oluşturulan sürekli kiriş hatları
    
    Returns:
        np.array of bool : Yasaklı sürekli kiriş hatları için maske

    Requires:
        numpy as np    
    """
    return np.array([i["banned"] for i in contBeam], dtype=bool)