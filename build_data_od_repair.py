import numpy as np
"""
Required by:
    build_data_od_mask_contBeam_beams
    build_data_od_mask_contBeam_colSpans
    build_od_mask_remove_colSpan_cols
    build_od_mask_remove_alone_col
    build_od_mask_remove_alone_colSpan
    build_od_mask_alone_beam
"""

import func_misc as misc
"""
Required by:
    apply_od_repair
"""





def build_data_od_mask_contBeam_beams(beamTopo, contBeamTopo, contBeam):
    """
    Sistemde bulunan bir sürekli hattın parçası olan kirişler için True;
    diğerleri için False döndürür.

    Args:
        beamTopo (np.ndarray)     : Sistemde bulunan kirişların topolojisi (1=var, 0=yok)
        contBeamTopo (np.ndarray) : Sistemde bulunan sürekli hatların topolojisi (1=var, 0=yok)
        contBeam (list)           : Sürekli hat bilgisi (build_contBeam'den gelir)

    Returns:
        Kiriş topolojisi için True/False maskesi

    Requires:
        numpy
    """

    # 1. Sistemde bulunan sürekli hatların indekslerini bul
    active_cont_indices = np.where(contBeamTopo == 1)[0]

    # 2️. Sistemde bulunan sürekli hatlara ait kirişlerinin indekslerini bul
    if active_cont_indices.size > 0:
        contBeam_beam_indices = np.concatenate([contBeam[i]["beam"] for i in active_cont_indices])
    else:
        contBeam_beam_indices = np.array([], dtype=int)

    # 3. Sistemde bulunan sürekli hatlara ait kirişler için True, diğerleri için False
    mask = np.isin(np.arange(len(beamTopo)), contBeam_beam_indices)

    return mask





def build_data_od_mask_contBeam_colSpans(colSpanTopo, contBeamTopo, contBeam):
    """
    Sistemde bulunan bir sürekli hattın parçası olan çizgisel kolonlar için True;
    diğerleri için False döndürür.

    Args:
        colSpanTopo (np.ndarray)  : Sistemde bulunan çizgisel kolonların topolojisi (1=var, 0=yok)
        contBeamTopo (np.ndarray) : Sistemde bulunan sürekli hatların topolojisi (1=var, 0=yok)
        contBeam (list)           : Sürekli hat bilgisi (build_contBeam'den gelir)

    Returns:
        Çizgisel kolon topolojisi için True/False maskesi

    Requires:
        numpy
    """

    # 1. Sistemde bulunan sürekli hatların indekslerini bul
    active_cont_indices = np.where(contBeamTopo == 1)[0]

    # 2️. Sistemde bulunan sürekli hatlara ait çizgisel kolonların indekslerini bul
    if active_cont_indices.size > 0:
        contBeam_colSpan_indices = np.concatenate([contBeam[i]["colSpan"] for i in active_cont_indices])
    else:
        contBeam_colSpan_indices = np.array([], dtype=int)

    # 3. Sistemde bulunan sürekli hatlara ait çizgisel kolonlar için True, diğerleri için False
    mask  = np.isin(np.arange(len(colSpanTopo)), contBeam_colSpan_indices)

    return mask





def build_od_mask_remove_colSpan_beams(colSpanTopo, beamTopo):
    """
    Bir aks parçasında hem çizgisel kolon (colSpanTopo==1) hem de kiriş (beamTopo==1)
    varsa ilgili aks parçası için True, aksi durumda False döner.

    Args:
        colSpanTopo (np.ndarray) : Çizgisel kolon varlık bilgisi (1=var, 0=yok)
        beamTopo (np.ndarray)    : Kiriş varlık bilgisi (1=var, 0=yok)

    Returns:
        np.ndarray: True/False maskesi
    
    Requires:
        none
    """
    return (colSpanTopo == 1) & (beamTopo == 1)





def build_od_mask_remove_colSpan_cols(colTopo, colSpanTopo, spans):
    """
    Eğer bir düğüm hem bir çizgisel kolonun (colSpanTopo==1) hem de
    bir noktasal kolonun (colTopo==1) üzerindeyse, o düğüm için True,
    aksi durumda False döner.

    Args:
        colTopo (np.ndarray)     : Noktasal kolon varlık bilgisi (1=var, 0=yok)
        colSpanTopo (np.ndarray) : Çizgisel kolon varlık bilgisi (1=var, 0=yok)
        spans (np.ndarray)       : Aks parçalarının başlangıç ve bitiş düğüm indeksleri
    
    Returns:
        np.ndarray: True/False maskesi
    
    Requires:
        numpy as np
    """
    mask = np.zeros(len(colTopo), dtype=bool)

    # 1. Üzerinde çizgisel kolon olan span'ları bul
    active_spans = np.where(colSpanTopo == 1)[0]
    # hiç çizgisel kolon yoksa hepsi False
    if active_spans.size == 0: return mask

    # 2. Bu spanların uç düğümlerini çıkar
    colSpan_nodes = spans[active_spans].ravel()

    # 3. Düğümlerin üzerinde noktasal kolon varsa bu düğümleri True yap.
    conflict_nodes = np.unique(colSpan_nodes[colTopo[colSpan_nodes] == 1])
    mask[conflict_nodes] = True

    return mask





def build_od_mask_remove_alone_col(colTopo, beamTopo, nodSpan):
    """
    Sistemde bulunan ve kendisine hiç kiriş bağlı olmayan noktasal kolonları
    tespit eder. Bu kolonların bulunduğu düğümler için True, diğerleri için False
    döner.

    Args:
        colTopo (np.ndarray)         : Noktasal kolon varlık bilgisi (1=var, 0=yok)
        beamTopo (np.ndarray)        : Kiriş varlık bilgisi (1=var, 0=yok)
        nodSpan (list of np.ndarray) : Her düğüme bağlı aks parçaları listesi

    Returns:
        np.ndarray: True/False maskesi

    Requires:
        numpy as np
    """
    # 1. Düğüm maskesini oluştur
    mask = np.zeros(len(colTopo), dtype=bool)

    # 2. Üzerinde noktasal kolon olan düğümleri bul
    col_nodes = np.where(colTopo == 1)[0]

    # 3. Üzerinde noktasal kolon olan bir düğüme bağlı kiriş yoksa → True
    for n in col_nodes:
        spans_of_node   = nodSpan[n]
        has_active_beam = np.any(beamTopo[spans_of_node] == 1)
        if not has_active_beam: mask[n] = True

    return mask





def build_od_mask_remove_alone_colSpan(colSpanTopo, beamTopo, spans, nodSpan):
    """
    Sistemde bulunan ve kendisine hiç kiriş bağlı olmayan çizgisel kolonları
    tespit eder. Bu kolonların bulunduğu aks parçaları için True, diğerleri
    için False döner.

    Args:
        colSpanTopo (np.ndarray)     : Çizgisel kolon varlık bilgisi (1=var, 0=yok)
        beamTopo (np.ndarray)        : Kiriş varlık bilgisi (1=var, 0=yok)
        spans (np.ndarray)           : Aks parçalarının başlangıç ve bitiş düğüm indeksleri
        nodSpan (list of np.ndarray) : Her düğüme bağlı aks parçaları listesi

    Returns:
        np.ndarray: True/False maskesi

    Requires:
        numpy as np
    """
    # 1. Aks parçası (span) maskesini oluştur
    mask = np.zeros(len(colSpanTopo), dtype=bool)

    # 2. Üzerinde çizgisel kolon bulunan aks parçalarını bul
    active_col_spans = np.where(colSpanTopo == 1)[0]

    # 3. Üzerinde çizgisel kolon bulunan aks parçaları için:
    for s in active_col_spans:
        n1, n2 = spans[s]

        # 3a. n1 düğümüne bağlı aktif kiriş var mı?
        has_beam_n1 = np.any(beamTopo[nodSpan[n1]] == 1)
        # 3b. n2 düğümüne bağlı aktif kiriş var mı?
        has_beam_n2 = np.any(beamTopo[nodSpan[n2]] == 1)

        # 3c. En az bir uçta aktif kiriş yoksa True
        if not (has_beam_n1 and has_beam_n2): mask[s] = True

    return mask





def build_od_mask_alone_beam(colTopo, colSpanTopo, beamTopo, spans):
    """
    Her iki ucu da serbest olan kirişler için maske oluşturur.
    Serbest = True, Tutulu = False
    Eğer aşağıdaki koşullardan biri sağlanıyorsa False:
        - Kirişin en az bir ucunda kolon varsa
        - Kirişin en az bir ucunda başka bir kiriş varsa
    
    Args:
        colTopo (np.ndarray)     : Noktasal kolon varlık bilgisi (1=var, 0=yok)
        colSpanTopo (np.ndarray) : Çizgisel kolon varlık bilgisi (1=var, 0=yok)
        beamTopo (np.ndarray)    : Kiriş varlık bilgisi (1=var, 0=yok)
        spans (np.ndarray)       : Aks parçalarının başlangıç ve bitiş düğüm indeksleri
    
    Returns:
        np.ndarray: True/False maskesi
    
    Requires:
        numpy as np
    """
    # 1. Tüm elemanları False olan maske oluştur
    mask = np.zeros(len(beamTopo), dtype=bool)

    # 2. Üzerinde kolon bulunan düğümler
    col_constrained = set(np.where(colTopo == 1)[0]) | set(spans[colSpanTopo == 1].ravel())

    # 3. Aktif kirişlerin uç düğümleri
    beam_nodes = spans[beamTopo == 1].ravel().tolist()

    for i in np.where(beamTopo == 1)[0]:

        n1, n2 = spans[i]
        
        # 4. Eğer kirişin en az bir ucunda kolon varsa devam et;
        #    diğer kontrollere gerek yok, False kalacak.
        if (n1 in col_constrained) or (n2 in col_constrained): continue

        # 5. Kirişin kendi uç düğümleri hariç diğer kirişlerin bağlı olduğu düğümler
        other_beam_nodes = beam_nodes.copy()
        # n1'i ve n2'yi yalnızca BİRER KEZ çıkar
        other_beam_nodes.remove(n1)
        other_beam_nodes.remove(n2)

        # 6. Diğer kirişler tarafından tutulan düğümleri bul
        other_beam_constrained = set(other_beam_nodes)

        # 7. Her iki uç da serbestse True
        if (n1 not in other_beam_constrained) and (n2 not in other_beam_constrained):
            mask[i] = True

    return mask





def build_data_od_repair(cand, geoData, contBeam):
    """
    Her çözüm adayı için tekrar oluşturulması gereken (on demand) onarım
    maskelerini oluşturur.

    Args:
        cand (list)     : Çözümün tasarım vektörü (manual_design_vector.md dosyasına bakınız)
        geoData (dict)  : Yapının geometrik verileri (build_data_geometry'den gelir)
        contBeam (list) : Sürekli hat bilgisi (build_contBeam'den gelir)

    Returns:
        On demand onarım maskelerini içeren sözlük

    Requires:
        none
    """
    colTopo      = cand[0]
    colSpanTopo  = cand[5]
    beamTopo     = cand[8]
    contBeamTopo = cand[11]

    spans   = geoData["spans"]
    nodSpan = geoData["nodSpan"]

    od_mask_contBeam_beams    = build_data_od_mask_contBeam_beams(beamTopo, contBeamTopo, contBeam)
    od_mask_contBeam_colSpans = build_data_od_mask_contBeam_colSpans(colSpanTopo, contBeamTopo, contBeam)
    od_mask_colspan_beams     = build_od_mask_remove_colSpan_beams(colSpanTopo, beamTopo)
    od_mask_colspan_cols      = build_od_mask_remove_colSpan_cols(colTopo, colSpanTopo, spans)
    od_mask_alone_col         = build_od_mask_remove_alone_col(colTopo, beamTopo, nodSpan)
    od_mask_alone_colspan     = build_od_mask_remove_alone_colSpan(colSpanTopo, beamTopo, spans, nodSpan)
    od_mask_alone_beam        = build_od_mask_alone_beam(colTopo, colSpanTopo, beamTopo, spans)

    return {
        "od_mask_contBeam_beams"    : od_mask_contBeam_beams,
        "od_mask_contBeam_colSpans" : od_mask_contBeam_colSpans,
        "od_mask_colspan_beams"     : od_mask_colspan_beams,
        "od_mask_colspan_cols"      : od_mask_colspan_cols,
        "od_mask_alone_col"         : od_mask_alone_col,
        "od_mask_alone_colspan"     : od_mask_alone_colspan,
        "od_mask_alone_beam"        : od_mask_alone_beam
    }





def apply_od_repair(cand, od_repair_mask):
    """
    cand listesine (çözüm adayı) build_data_od_repair fonksiyonu ile elde edilen onarım maskelerini
    (od_repair_mask) uygular.

    Args:
        cand (list)           : Çözümün tasarım vektörü (manual_design_vector.md dosyasına bakınız)
        od_repair_mask (dict) : build_data_od_repair fonksiyonu ile elde edilen onarım maskeleri

    Returns:
        list: cand listesinin onarım maskeleri uygulanmış yeni bir kopyası
    
    Requires:
        func_misc as misc
    """
    mask_list = [
        #! Bunu normalde tercihe bağlı olarak planlamıştım;
        #! ama burada zorunlu yapıyorum
        #! -----------------------------------------
        od_repair_mask["od_mask_contBeam_beams"],
        od_repair_mask["od_mask_contBeam_colSpans"],
        #! -----------------------------------------
        od_repair_mask["od_mask_colspan_beams"],
        od_repair_mask["od_mask_colspan_cols"],
        od_repair_mask["od_mask_alone_col"],
        od_repair_mask["od_mask_alone_colspan"],
        od_repair_mask["od_mask_alone_beam"]
    ]
    
    # beamTopo, colSpanTopo, beamTopo, colTopo, colTopo, colSpanTopo, beamTopo
    # maskesi vardır. Bu sebeple idx_list aşağıdaki gibi olmalıdır.
    idx_list = [8, 5, 8, 0, 0, 5, 8]

    option_list = [
        "True_is_1",
        "True_is_1",
        "True_is_0",
        "True_is_0",
        "True_is_0",
        "True_is_0",
        "True_is_0"
    ]

    return misc.apply_masks(cand, idx_list, mask_list, option_list)