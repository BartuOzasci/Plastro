import ezdxf
"""
Required by:
    read_dxf_file
"""

import numpy as np
"""
Required by:
    extract_points
    extract_lines
    extract_polygons
    extract_texts
"""





def read_dxf_file(file_name: str):
    """
    Verilen DXF dosyasını okur ve model (çizim) alanını döndürür

    Args:
        file_name (str): okunacak DXF dosyasının yolu
    
    Returns:
        ezdxf.modelspace: DXF dosyasının model (çizim) alanı

    Requires:
        ezdxf
    """
    try:
        dxf = ezdxf.readfile(file_name)
        return dxf.modelspace()
    except:
        raise ValueError("DXF dosyası okunamadı.")





def extract_points(modelspace, layer_name: str):
    """
    Verilen DXF model (çizim) alanından belirtilen katmandaki noktaları döndürür.

    Args:
        modelspace: DXF dosyasının modelspace (çizim alanı)
        layer_name (str): Noktaların bulunduğu katman adı

    Returns:
        numpy.ndarray: Noktaların [x, y] koordinatlarını içeren numpy dizisi.
                       Örn: [[x1, y1], [x2, y2], ...]
    Requires:
        numpy
    """
    points = modelspace.query(f'POINT[layer == "{layer_name}"]')
    
    coords = np.array([
        [pt.dxf.location.x, pt.dxf.location.y]
        for pt in points])
    
    return coords





def extract_lines(modelspace, layer_name: str):
    """
    Verilen DXF model (çizim) alanından belirtilen katmandaki çizgileri döndürür.

    Args:
        modelspace: DXF dosyasının model (çizim) alanı
        layer_name (str): Çizgilerin bulunduğu katman adı

    Returns:
        numpy.ndarray: Çizgilerin başlangıç ve bitiş noktalarını içeren numpy dizisi
                       [ [[x1,y1],[x2,y2]] , [[x3,y3],[x4,y4]] , ... ]

    Requires:
        numpy
    """
    lines = modelspace.query(f'LINE[layer == "{layer_name}"]')
    
    lines = np.array([
        [
            [line.dxf.start.x , line.dxf.start.y],
            [line.dxf.end.x   , line.dxf.end.y  ]
        ] for line in lines])
    
    return lines





def extract_polygons(modelspace, layer_name: str):
    """
    Verilen DXF model (çizim) alanından poligonların köşe koordinatlarını döndürür.

    Args:
        modelspace: DXF dosyasının model (çizim) alanı
        layer_name (str): Poligonların bulunduğu katman adı

    Returns:
        list of numpy.ndarrays: Poligonların köşe koordinatlarını içeren numpy dizileri listesi.

    Requires:
        numpy
    """
    polygons = modelspace.query(f'LWPOLYLINE[layer == "{layer_name}"]')
    
    polygons = [np.array(i.get_points())[:, :2] for i in polygons]
    
    return polygons





def extract_texts(modelspace, layer_name: str):
    """
    Verilen DXF model (çizim) alanından belirtilen katmandaki metinleri döndürür.

    Args:
        modelspace: DXF dosyasının modelspace (çizim alanı)
        layer_name (str): Metinlerin bulunduğu katman adı

    Returns:
        list of dicts: Her bir metin için sözlük içeren bir liste
    
    Requires:
        numpy
    """
    texts = modelspace.query(f'MTEXT[layer == "{layer_name}"]')

    texts = [{
        "text"     : text.dxf.text,
        "position" : np.array([text.dxf.insert.x, text.dxf.insert.y])
    } for text in texts]

    return texts





def read_DXF(file_name: str):
    """
    Verilen DXF dosyasını okur ve plastro çizim bileşenlerini döner.

    Args:
        file_name (str): okunacak DXF dosyasının yolu
    
    Returns:
        dict: DXF dosyasından okunan plastro bileşenlerini içeren sözlük

    Requires:
        None
    """
    modelspace = read_dxf_file(file_name)

    axes            = extract_lines(modelspace, "plastro_axes")
    basePol_points  = extract_polygons(modelspace, "plastro_basePol")
    floorPol_points = extract_polygons(modelspace, "plastro_floorPol")
    areas_points    = extract_polygons(modelspace, "plastro_areas")

    areaClasses     = extract_texts(modelspace, "plastro_areaClasses")
    walls           = extract_lines(modelspace, "plastro_walls")

    alwaysCol       = extract_points(modelspace, "plastro_alwaysCol")
    alwaysColSpan   = extract_points(modelspace, "plastro_alwaysColSpan")
    alwaysBeam      = extract_points(modelspace, "plastro_alwaysBeam")

    neverCol        = extract_points(modelspace, "plastro_neverCol")
    neverColPart    = extract_lines(modelspace, "plastro_neverColPart")
    neverColSpan    = extract_points(modelspace, "plastro_neverColSpan")
    neverBeam       = extract_points(modelspace, "plastro_neverBeam")

    return {
        "axes"            : axes,
        "basePol_points"  : basePol_points,
        "floorPol_points" : floorPol_points,
        "areas_points"    : areas_points,

        "areaClasses"     : areaClasses,
        "walls"           : walls,

        "alwaysCol"       : alwaysCol,
        "alwaysColSpan"   : alwaysColSpan,
        "alwaysBeam"      : alwaysBeam,

        "neverCol"        : neverCol,
        "neverColPart"    : neverColPart,
        "neverColSpan"    : neverColSpan,
        "neverBeam"       : neverBeam
    }