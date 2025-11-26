import numpy as np
"""
Required by:
    calc_colSecProp
    calc_colRotated
    calc_colPlaced
    calc_colSpanProp
    calc_colSpanRotated
    calc_colSpanPlaced
    calc_beamPlaced
    calc_slabProp
    calc_slabPlaced
"""

import func_geo_basic as geoBasic
"""
Required by:
    calc_slabProp
"""





def calc_colSecProp(colSec):
    """
    Ayarlar (xls) dosyasından okunan colSec noktasal kolon kesiti bilgilerinden
    faydalanarak kesitlerin köşe koordinatlarını, alanlarını ve atalet momentlerini
    hesaplar.
    
    Args:
        colSec : Ayarlar (xls) dosyasından okunan colSec sözlüğü
    
    Returns:
        dict : Kesitlerin boyutlarını, köşe koordinatlarını, alanlarını ve atalet
               momentlerini içeren sözlük
    
    Requires:
        numpy
    """
    dL = colSec["dL"].astype(float)
    dS = colSec["dS"].astype(float)
    
    # Kesitlerin köşe koordinatlarını bulur. Kesit daire ise ilgili yere
    # dairenin çapını yazar.
    is_circle = np.isnan(dS)
    coords    = np.empty(len(dL), dtype=object)
    
    for i in range(len(dL)):
        if is_circle[i]: coords[i] = dL[i]
        else:
            L, S = dL[i], dS[i]
            coords[i] = np.array([
                [L/2,  S/2],
                [L/2, -S/2],
                [-L/2, -S/2],
                [-L/2,  S/2],
                [L/2,  S/2]
            ])
    
    # A   : Kesit Alanı
    A   = np.where(is_circle, np.pi*dL**2/4, dL*dS)
    # I_L : Uzun kenara PARALEL eksen etrafındaki atalet momenti
    I_L = np.where(is_circle, np.pi*dL**4/64, dL*dS**3/12)    
    # I_S : Uzun kenara DİK eksen etrafındaki atalet momenti
    I_S = np.where(is_circle, np.pi*dL**4/64, dS*dL**3/12)
    
    return {
        "dL"     : dL,
        "dS"     : dS,
        "coords" : coords,
        "A"      : A,
        "I_L"    : I_L,
        "I_S"    : I_S
    }





def calc_colRotated(colTopo, colSize, colDirec, axesAngle, nodAx, colSecProp):
    """
    Döndürülmüş kolon kesit özelliklerini hesaplar.

    Args:
        colTopo    : Kolon topolojisi vektörü
        colSize    : Kolon kesitleri vektörü
        colDirec   : Kolon yönleri vektörü
        axesAngle  : Aks açılarını [açı, sin, cos] şeklinde tutan dizi
        nodAx      : Her bir düğümden geçen aksları içeren liste
        colSecProp : Kolon kesit özellikleri sözlüğü {dL, dS, coords, A, I_L, I_S}
    
    Returns:
        dict       : Döndürülmüş kesit özellikleri {dL, dS, sinCos, coords, A, Ix, Iy}

    Requires:
        numpy
    """
    # Döndürülmüş kesit özellikleri için boş diziler oluştur
    n          = len(colTopo)
    dL         = np.full(n, np.nan, dtype=float)
    dS         = np.full(n, np.nan, dtype=float)
    sinCos     = np.full(n, np.nan, dtype=object)
    coords_rot = np.full(n, np.nan, dtype=object)
    A          = np.full(n, np.nan, dtype=float)
    Ix         = np.full(n, np.nan, dtype=float)
    Iy         = np.full(n, np.nan, dtype=float)

    # Eğer kolon sistemde yoksa devam et
    for i in range(n):
        if not colTopo[i] == 1: continue
        
        # Döndürülmemiş kesit özelliklerini al
        sec_idx = colSize[i]
        dL_val  = colSecProp["dL"][sec_idx]
        dS_val  = colSecProp["dS"][sec_idx]
        coords  = colSecProp["coords"][sec_idx]
        A_val   = colSecProp["A"][sec_idx]
        I_L     = colSecProp["I_L"][sec_idx]
        I_S     = colSecProp["I_S"][sec_idx]

        # Kesit boyutlarını ilgili dizilere yaz
        dL[i], dS[i] = dL_val, dS_val
        # Kolon aksının sin ve cos bileşenlerini ilgili diziye yaz
        aks_idx      = nodAx[i][colDirec[i]]
        sin_p, cos_p = axesAngle[aks_idx][1], axesAngle[aks_idx][2]
        sinCos[i]    = np.array([sin_p, cos_p])

        # Eğer kesit daire ise döndürülmüş kesit özellikleri
        # döndürülmemiş kesit özellikleri ile aynıdır.
        if np.isscalar(coords):
            coords_rot[i] = coords
            Ix[i]         = I_L
            Iy[i]         = I_S
            A[i]          = A_val
            continue
        
        # Eğer kesit dikdörtgen ise döndürülmüş koordinatları hesapla
        R_coords      = np.array([[cos_p, -sin_p], [sin_p,  cos_p]])
        coords_rot[i] = coords @ R_coords.T
        
        # Eğer kesit dikdörtgen ise döndürülmüş atalet momentlerini hesapla
        sin_n, cos_n = -sin_p, cos_p # negatif açının sin ve cos bileşenleri
        Ix[i]        = I_L * cos_n**2 + I_S * sin_n**2
        Iy[i]        = I_L * sin_n**2 + I_S * cos_n**2

        # Döndürülmüş alan ile döndürülmemiş alan aynıdır.
        A[i] = A_val

    return {
        "dL"     : dL,
        "dS"     : dS,
        "sinCos" : sinCos,
        "coords" : coords_rot,
        "A"      : A,
        "Ix"     : Ix,
        "Iy"     : Iy
    }





def calc_colPlaced(colTopo, colEccL, colEccS, nodes, colRotated):
    """
    Noktasal kolon koordinatlarını eksantrikliklere göre kaydırır ve
    ilgili düğüme taşır.
    
    Args:
        colTopo    : Kolon topolojisi vektörü
        colEccL    : Uzun kenar doğrultusunda kolon eksantrikliği vektörü
        colEccS    : Uzun kenara DİK doğrultuda kolon eksantrikliği vektörü
        nodes      : Düğümlerin koordinatlarını içeren numpy dizisi
        colRotated : Döndürülmüş kolon bilgileri sözlüğü {dL, dS, sinCos, coords, A, Ix, Iy}
    
    Returns:
        Kaydırılmış ve taşınmış kolon koordinatlarını da içeren sözlük
        {dL, dS, sinCos, coords center, coords, A, Ix, Iy}

    Requires:
        numpy
    """
    dL, dS = colRotated["dL"], colRotated["dS"]
    sinCos = colRotated["sinCos"]
    coords = colRotated["coords"]

    n = len(colTopo)
    coords_center  = np.full(n, np.nan, dtype=object)
    coords_shifted = coords.copy()

    for i in range(n):
        # Eğer kolon yoksa devam et
        if not colTopo[i] == 1: continue

        para_vec = np.array([sinCos[i][1], sinCos[i][0]]) # L yönü
        perp_vec = np.array([-sinCos[i][0], sinCos[i][1]]) # L yönüne dik yön

        # Eğer kesit daire ise
        if np.isnan(dS[i]):
            # Kaydır ve ilgili düğüme taşı
            offset_L = para_vec * (colEccL[i] * dL[i])
            offset_S = perp_vec * (colEccS[i] * dL[i])
            center   = nodes[i] + offset_L + offset_S
            
            coords_center[i], coords_shifted[i] = center, center
        
        # Eğer kesit dikdörtgen ise
        else:
            # Kaydır ve ilgili düğüme taşı
            offset_L = para_vec * (colEccL[i] * dL[i])
            offset_S = perp_vec * (colEccS[i] * dS[i])
            center   = nodes[i] + offset_L + offset_S

            coords_center[i], coords_shifted[i] = center, coords[i] + center

    return {
        "dL"            : dL,
        "dS"            : dS,
        "sinCos"        : sinCos,
        "coords center" : coords_center,
        "coords"        : coords_shifted,
        "A"             : colRotated["A"],
        "Ix"            : colRotated["Ix"],
        "Iy"            : colRotated["Iy"]
    }





def calc_colSpanProp(colSpanTopo, colSpanSize, spanLen, colSpanSec):
    """
    Ayarlar (xls) dosyasından okunan colSpanSec çizgisel kolon kesiti bilgilerinden
    faydalanarak kesitlerin köşe koordinatlarını, alanlarını ve atalet momentlerini
    hesaplar.
    
    Args:
        colSpanTopo : Çizgisel kolon topolojisi vektörü
        colSpanSize : Çizgisel kolon kesitleri vektörü
        spanLen     : Aks parçalarının uzunluklarını tutan dizi
        colSpanSec  : Ayarlar (xls) dosyasından okunan colSpanSec sözlüğü
    
    Returns:
        dict : Kesitlerin boyutlarını, köşe koordinatlarını, alanlarını ve atalet
               momentlerini içeren sözlük {dL, dS, coords, A, I_L, I_S}

    Requires:
        numpy
    """
    n      = len(colSpanTopo)
    dL     = np.full(n, np.nan)
    dS     = np.full(n, np.nan)
    coords = np.full(n, np.nan, dtype=object)
    A      = np.full(n, np.nan)
    I_L    = np.full(n, np.nan)
    I_S    = np.full(n, np.nan)
    
    for i in range(n):
        if colSpanTopo[i] == 1:
            dL[i] = spanLen[i] # Çizgisel kolonun uzun kenarı
            dS[i] = colSpanSec["width"][colSpanSize[i]] # kısa kenarı
            
            # Köşe koordinatları
            #! her span için münmkün olan tüm çizgisel kolon genişlikleri göz önünde
            #! bulundurularak bir liste önceden hazırlanıp, koordinat, A, I_L ve I_S
            #! hesaplamaları için kullanılabilir mi acaba? Yoksa gereksiz mi?
            coords[i] = np.array([
                [ dL[i]/2,  dS[i]/2],
                [ dL[i]/2, -dS[i]/2],
                [-dL[i]/2, -dS[i]/2],
                [-dL[i]/2,  dS[i]/2],
                [ dL[i]/2,  dS[i]/2]
            ])
            
            # A   : Kesit alanı
            A[i]   = dL[i] * dS[i]
            # I_L : Uzun kenara PARALEL eksen etrafındaki atalet momenti
            I_L[i] = dL[i] * dS[i]**3 / 12
            # I_S : Uzun kenara DİK eksen etrafındaki atalet momenti
            I_S[i] = dS[i] * dL[i]**3 / 12
    
    return {
        "dL"     : dL,
        "dS"     : dS,
        "coords" : coords,
        "A"      : A,
        "I_L"    : I_L,
        "I_S"    : I_S
    }





def calc_colSpanRotated(colSpanTopo, axesAngle, spanAx, colSpanProp):
    """
    Döndürülmüş çizgisel kolon kesit özelliklerini hesaplar.

    Args:
        colSpanTopo : Çizgisel kolon topolojisi vektörü
        axesAngle   : Aks açılarını [açı, sin, cos] şeklinde tutan dizi
        spanAx      : Hangi aks parçasının hangi aks üzerinde olduğu bilgisini tutan dizi
        colSpanProp : Çizgisel kolon kesit özellikleri sözlüğü {dL, dS, coords, A, I_L, I_S}
    
    Returns:
        dict        : Döndürülmüş kesit özellikleri {dL, dS, sinCos, coords, A, Ix, Iy}

    Requires:
        numpy
    """
    dL, dS   = colSpanProp["dL"], colSpanProp["dS"]
    coords   = colSpanProp["coords"]
    A        = colSpanProp["A"]
    I_L, I_S = colSpanProp["I_L"], colSpanProp["I_S"]


    n          = len(colSpanTopo)
    sinCos     = np.full((n, 2), np.nan)
    coords_rot = np.full(n, np.nan, dtype=object)
    Ix         = np.full(n, np.nan)
    Iy         = np.full(n, np.nan)
    
    for i in range(n):
        # Eğer çizgisel kolon yoksa devam et
        if not colSpanTopo[i] == 1: continue
        
        # Çizgisel kolon doğrultusunun sin ve cos bileşenleri
        _, sin_p, cos_p = axesAngle[spanAx[i]]
        sinCos[i] = np.array([sin_p, cos_p])
        
        # Rotasyon matrisi (2x2)
        R = np.array([[cos_p, -sin_p], [sin_p,  cos_p]])
        # Döndürülmüş çizgisel kolon koordinatları
        coords_rot[i] = coords[i] @ R.T
        
        # Negatif açı ile döndürülmüş atalet momentleri
        sin_n, cos_n = -sin_p, cos_p
        Ix[i] = I_L[i] * cos_n**2 + I_S[i] * sin_n**2
        Iy[i] = I_L[i] * sin_n**2 + I_S[i] * cos_n**2

    return {
        "dL"     : dL,
        "dS"     : dS,
        "sinCos" : sinCos,
        "coords" : coords_rot,
        "A"      : A,
        "Ix"     : Ix,
        "Iy"     : Iy
    }





def calc_colSpanPlaced(colSpanTopo, colSpanEcc, spansG, colSpanRotated):
    """
    Çizgisel kolon koordinatlarını eksantrikliklere göre kaydırır ve
    ilgili düğüme taşır.
    
    Args:
        colSpanTopo    : Çizgisel kolon topolojisi vektörü
        colSpanEcc     : Çizgisel kolon eksantrikliği vektörü
        spansG         : Aks parçalarının geometrik merkezlerinin koordinatlarını içeren numpy dizisi
        colSpanRotated : Döndürülmüş kolon bilgileri sözlüğü {dL, dS, sinCos, coords, A, Ix, Iy}
    
    Returns:
        Kaydırılmış ve taşınmış çizgisel kolon koordinatlarını da içeren sözlük
        {dL, dS, sinCos, coords center, coords, A, Ix, Iy}

    Requires:
        numpy
    """
    dL, dS = colSpanRotated["dL"], colSpanRotated["dS"]
    sinCos = colSpanRotated["sinCos"]
    coords = colSpanRotated["coords"]
    A      = colSpanRotated["A"]
    Ix     = colSpanRotated["Ix"]
    Iy     = colSpanRotated["Iy"]

    n              = len(colSpanTopo)
    coords_center  = np.full((n, 2), np.nan)
    coords_shifted = np.full(n, np.nan, dtype=object)

    for i in range(n):
        # Eğer çizgisel kolon yoksa devam
        if not colSpanTopo[i] == 1: continue
        
        # Çizgisel kolon eksenine dik vektör : (-sin, cos)
        perp_vec = np.array([-sinCos[i][0], sinCos[i][1]])

        shift     = dS[i] * colSpanEcc[i] # Kaydırma miktarı
        shift_vec = perp_vec * shift # Kaydırma vektörü

        # Koordinatları kaydır ve ilgili düğümlere taşı
        center            = spansG[i] + shift_vec
        coords_center[i]  = center
        coords_shifted[i] = coords[i] + center

    return {
        "dL"            : dL,
        "dS"            : dS,
        "sinCos"        : sinCos,
        "coords center" : coords_center,
        "coords"        : coords_shifted,
        "A"             : A,
        "Ix"            : Ix,
        "Iy"            : Iy
    }





def calc_beamPlaced(beamTopo, beamSize, beamEcc, axesAngle, nodes, spans, spanAx, spansG, beamSec):
    """
    Sistemdeki kirişlerin kesit özelliklerini ve koordinatlarını hesaplar.

    Args:
        beamTopo  : Kiriş topolojisi vektörü
        beamSize  : Kiriş kesitleri vektörü
        beamEcc   : Kiriş eksenine DİK doğrultuda kiriş eksantrikliği vektörü
        axesAngle : Aks açılarını [açı, sin, cos] şeklinde tutan dizi
        nodes     : Düğümlerin koordinatlarını içeren numpy dizisi
        spans     : Aks parçalarının başlangıç ve bitiş düğümlerini içeren numpy dizisi
        spanAx    : Hangi aks parçasının hangi aks üzerinde olduğu bilgisini tutan dizi
        spansG    : Aks parçalarının geometrik merkezlerinin koordinatlarını içeren numpy dizisi
        beamSec   : Ayarlar (xls) dosyasından okunan beamSec sözlüğü
    
    Returns:
        dict      : Kirişlerin kesit özelliklerini ve koordinatlarını içeren sözlük
                    {b, h, Ix, center, beam axis, bounds, coords}
    
    Requires:
        numpy
    """
    n         = len(spans)
    b         = np.full(n, np.nan)
    h         = np.full(n, np.nan)
    Ix        = np.full(n, np.nan)
    center    = np.full(n, np.nan, dtype=object)
    beam_axis = np.full(n, np.nan, dtype=object)
    bounds    = np.full(n, np.nan, dtype=object)
    coords    = np.full(n, np.nan, dtype=object)

    for i in range(n):
        # Kiriş sistemde yoksa atla
        if not beamTopo[i] == 1: continue

        b_val             = beamSec["b"][beamSize[i]] # kiriş genişliği
        h_val             = beamSec["h"][beamSize[i]] # kiriş derinliği
        #! bu satırda da gereksiz tekrarlı hesaplar yapılıyor.
        #! tüm seçilebilecek kesitler için b, h ve Ix değerleri daha önceden hesaplanıp
        #! bir listede tutulabilir.
        b[i], h[i], Ix[i] = b_val, h_val, b_val*h_val**3/12 # kiriş kesit özellikleri

        shift_dist      = beamEcc[i] * b_val # kaydırma mesafesi
        _, sin_a, cos_a = axesAngle[spanAx[i]] # kiriş aksının sin ve cos bileşenleri
        nvec            = np.array([-sin_a, cos_a]) # kiriş aksına dik yön
        shift_vec       = nvec * shift_dist # kaydırma vektörü

        # Kaydırılmış kiriş merkezi
        center[i] = spansG[i] + shift_vec

        # Kaydırılmış kiriş ekseni
        n1, n2       = spans[i]
        p1           = nodes[n1] + shift_vec
        p2           = nodes[n2] + shift_vec
        beam_axis[i] = np.array([p1, p2])

        # Kirişi sınırlayan eksen doğrultusunda çizgiler
        offset      = nvec * (b_val / 2.0)
        bound_upper = np.array([p1 + offset, p2 + offset])
        bound_lower = np.array([p1 - offset, p2 - offset])
        bounds[i]   = np.array([bound_upper, bound_lower])

        # Kiriş plan (üst görünüş) koordinatları
        coords[i] = np.array([
            bound_upper[1], # sağ üst
            bound_lower[1], # sağ alt
            bound_lower[0], # sol alt
            bound_upper[0], # sol üst
            bound_upper[1]  # sağ üst
        ])

    return {
        "b"         : b,
        "h"         : h,
        "Ix"        : Ix,
        "center"    : center,
        "beam axis" : beam_axis,
        "bounds"    : bounds,
        "coords"    : coords
    }





def calc_slabProp(geoData, dxf, xls):
    """
    areas dizisi ile tanımlanan alanlarda bulunan döşemelerin özelliklerini döndürür.

    Args:
        geoData : Sistemin temel geometrik verisi (build_data_geo)
        dxf     : read_DXF.read_DXF ile okunan çizim (dxf) dosyası
        xls     : read_XLS.read_XLS ile okunan ayarlar (xls) dosyası

    Returns:
        dict: Döşemelerin özelliklerini içeren sözlük
        {coords, class, no columns, no beams, no slab, importance}

    Requires:
        numpy
        func_geo_basic as geoBasic
    """
    # Değişkenlere değerleri ata
    areas        = geoData["areas"]
    nodes        = geoData["nodes"]
    areas_points = dxf["areas_points"]
    areaClasses  = dxf["areaClasses"]
    areaProp     = xls["areaProp"]

    # Döşemelerin sınıflarını bul
    class_text_pos  = np.array([i["position"] for i in areaClasses])
    area_classes    = []

    for i, poly_nodes in enumerate(areas):
        inside_mask    = geoBasic.nodes_in_polygon(class_text_pos, poly_nodes, nodes)
        first_true_idx = np.argmax(inside_mask)
        area_classes.append(areaClasses[first_true_idx]["text"])
    area_classes = np.array(area_classes, dtype=int)

    # Sınıfları tespit edilen döşemelerin özelliklerini bul
    no_columns, no_beams, no_slab, importance = [], [], [], []
    
    for i in area_classes:
        class_idx = np.where(areaProp["class"] == i)[0][0]
        no_columns.append(areaProp["no columns"][class_idx])
        no_beams.append(areaProp["no beams"][class_idx])
        no_slab.append(areaProp["no slab"][class_idx])
        importance.append(areaProp["importance"][class_idx])
    
    # Sonuçları sözlük halinde döndür
    return {
        "coords"     : areas_points,
        "class"      : area_classes,
        "no columns" : np.array(no_columns, dtype=int),
        "no beams"   : np.array(no_beams, dtype=int),
        "no slab"    : np.array(no_slab, dtype=int),
        "importance" : np.array(importance, dtype=float)
    }





def calc_slabPlaced(slabSize, slabProp, slabSec):
    """
    Sistemde bulunan döşemelerin bilgilerini döndürür.

    Args:
        slabSize : Döşeme kalınlıkları vektörü
        slabProp : Döşeme özellikleri sözlüğü
                   {coords, class, no columns, no beams, no slab, importance}
        slabSec : Ayarlar (xls) dosyasından okunan slabSec sözlüğü

    Returns:
        dict : Sistemde bulunan döşeme bilgileri sözlüğü
               {h, coords, class, no columns, no beams, no slab, importance}

    Requires:
        numpy
    """
    # Eğer döşeme varsa döşeme kalınlığını yaz,
    # yoksa döşeme kalınlığını np.nan olarak belirle
    h = np.where(
        slabProp["no slab"] == 1, 
        np.nan, 
        slabSec["h"][slabSize]
    )

    # slabPlaced sözlüğününün slabProp sözlüğünden tek farkı
    # döşeme kalınlığı bilgisini de içermesidir.
    slabPlaced = {
        "h": h,
        "coords": slabProp["coords"],
        "class": slabProp["class"],
        "no columns": slabProp["no columns"],
        "no beams": slabProp["no beams"],
        "no slab": slabProp["no slab"],
        "importance": slabProp["importance"]
    }
    
    return slabPlaced





def build_data_struct(designVec, xls, geoData, colSecProp, slabProp):
    """
    Taşıyıcı sistem elemanları ile ilgili yapısal bilgileri döndürür.

    Args:
        designVec  : Tasarım vektörü (manual_design_vector.md)
        xls        : read_XLS.read_XLS ile okunan ayarlar (xls) dosyası
        geoData    : Sistemin temel geometrik verisi (build_data_geo)
        colSecProp : calc_colSecProp ile hesaplanan kolon kesit özellikleri
        slabProp   : calc_slabProp ile hesaplanan döşeme özellikleri

    Returns:
        dict: Taşıyıcı sistem elemanları ile ilgili yapısal bilgileri içeren sözlük
              {col, colSpan, beam, slab}

    Requires:
        None
    """
    colTopo      = designVec[0]
    colSize      = designVec[1]
    colDirec     = designVec[2]
    colEccL      = designVec[3]
    colEccS      = designVec[4]
    colSpanTopo  = designVec[5]
    colSpanSize  = designVec[6]
    colSpanEcc   = designVec[7]
    beamTopo     = designVec[8]
    beamSize     = designVec[9]
    beamEcc      = designVec[10]
    slabSize     = designVec[12]

    colSpanSec   = xls["colSpanSec"]
    beamSec      = xls["beamSec"]
    slabSec      = xls["slabSec"]

    axesAngle    = geoData["axesAngle"]
    nodes        = geoData["nodes"]
    nodAx        = geoData["nodAx"]
    spans        = geoData["spans"]
    spanAx       = geoData["spanAx"]
    spanLen      = geoData["spanLen"]
    spansG       = geoData["spansG"]
    
    colRotated     = calc_colRotated(colTopo, colSize, colDirec, axesAngle, nodAx, colSecProp)
    colPlaced      = calc_colPlaced(colTopo, colEccL, colEccS, nodes, colRotated)

    colSpanProp    = calc_colSpanProp(colSpanTopo, colSpanSize, spanLen, colSpanSec)
    colSpanRotated = calc_colSpanRotated(colSpanTopo, axesAngle, spanAx, colSpanProp)
    colSpanPlaced  = calc_colSpanPlaced(colSpanTopo, colSpanEcc, spansG, colSpanRotated)

    beamPlaced     = calc_beamPlaced(beamTopo, beamSize, beamEcc, axesAngle, nodes, spans, spanAx, spansG, beamSec)

    slabPlaced     = calc_slabPlaced(slabSize, slabProp, slabSec)

    return {
        "col"     : colPlaced,
        "colSpan" : colSpanPlaced,
        "beam"    : beamPlaced,
        "slab"    : slabPlaced
    }