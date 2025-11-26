import numpy as np
"""
Required by:
    draw_member_groups
"""

import matplotlib.collections as mcoll
"""
Required by:
    draw_member_groups
"""

import matplotlib.patches as patches
"""
Required by:
    draw_member_groups
"""

import draw_basic_geometry as drawBasic
"""
Required by:
    draw_struct_members
"""

import os
"""
Required by:
    draw_struct_members
"""





def draw_member_groups(
        ax,
        data_struct, member_groups=["col", "colSpan", "beam", "slab"],
        alpha=1, zorder=7, hatchScale=1
    ):
    """
    draw_basic_geometry ile oluşturulan çizim üzerine yapı elemanlarını çizer

    Args:
        ax            : Matplotlib eksen nesnesi
        data_struct   : Yapı elemanları verisi
        member_groups : Çizilmesi istenen eleman gruplarını içeren liste
                        ["col", "colSpan", "beam" ve "slab"]
        alpha         : En opak yapısal eleman sınıfının opaklık derecesi (0-1)
        zorder        : En üstteki yapısal eleman sınıfının çizim sırası
        hatchScale    : Kolonlar için tarama çizgisi ölçeği
    
    Returns:
        None
    
    Requires:
        numpy as np
        matplotlib.collections as mcoll
        matplotlib.patches as patches
    """

    face_dict   = {"col": "red", "colSpan": "purple", "beam": "green", "slab": "blue"}
    alpha_dict  = {"col": alpha, "colSpan": alpha*0.5, "beam": alpha*0.8, "slab": alpha*0.6}
    zorder_dict = {"col": zorder, "colSpan": zorder, "beam": zorder-1, "slab": zorder-2}

    hatchType   = "/" # ("/", "\\", "|", "-", "+", "x", "o", "O", ".", "*") olabilir
    hatch       = hatchType * int(hatchScale)
    hatch_dict  = {"col": hatch, "colSpan": hatch, "beam": None, "slab": None}

    # Poligon yapı elemanlarının çizimi için döngü
    for group in member_groups:
        grp_dict = data_struct[group]
        polygons = grp_dict["coords"] # Ham poligon köşe koordinatları dizisi

        # Eğer sıra noktasal kolonlara geldi ise sadece dikdörtgen olan kolonları al
        if group == "col":
            mask_rect = (~np.isnan(grp_dict["dL"])) & (~np.isnan(grp_dict["dS"]))
            polygons  = polygons[mask_rect]

        # np.nan değerlerini temizleyerek çizim listesini oluştur.
        polygons = [x for x in polygons if not (isinstance(x, float) and np.isnan(x))]

        ax.add_collection(mcoll.PolyCollection(
            polygons,
            facecolors = face_dict[group],   # Arka plan rengi
            edgecolors = "black",            # Kenarlık ve tarama çizgilerinin rengi
            linestyles = "-",                # Kenarlık stili
            linewidths = 2,                  # Kenarlık ve tarama çizgilerinin kalınlığı
            alpha      = alpha_dict[group],  # Opaklık (0-1 arası)
            zorder     = zorder_dict[group], # Çizim sırası
            hatch      = hatch_dict[group]   # Tarama çizgileri
        ))

    # Dairesel noktasal kolonların çizimi
    if "col" in member_groups:
        # Dairesel kolonların merkez ve çap bilgilerini çıkar
        # Bu aşamada np.nan değerlerini temizleme gibi bir işleme gerek yoktur.
        grp_dict    = data_struct["col"]
        mask_circle = (~np.isnan(grp_dict["dL"])) & (np.isnan(grp_dict["dS"]))
        centers     = grp_dict["coords center"][mask_circle]
        diameters   = grp_dict["dL"][mask_circle]

        # Çizim listesini oluştur
        circles = [patches.Circle(c, radius=d/2) for c, d in zip(centers, diameters)]

        ax.add_collection(mcoll.PatchCollection(
            circles,
            facecolor = face_dict["col"],   # Arka plan rengi
            edgecolor = "black",            # Kenarlık ve tarama çizgilerinin rengi
            linestyle = "-",                # Kenarlık stili
            linewidth = 2,                  # Kenarlık ve tarama çizgilerinin kalınlığı
            alpha     = alpha_dict["col"],  # Opaklık (0-1 arası)
            zorder    = zorder_dict["col"], # Çizim sırası
            hatch     = hatch_dict["col"]   # Tarama çizgileri
        ))









def draw_struct_members(
        basic_geometry,
        data_struct,
        action="none", fileName="_output.png",
        member_groups=["col", "colSpan", "beam", "slab"], alpha=1, zorder=7, hatchScale=1
    ):
    """
    basic_geometry üzerine yapısal elemanların çizimlerini ekler.

    Args:
        basic_geometry : draw_basic_geometry ile oluşturulan fig, ax nesneleri
        data_struct    : Yapı elemanları verisi
        action         : "none", "show" veya "save" olarak belirlenir
        fileName       : Çıktı dosya adı (sadece "save" için geçerli)
        member_groups  : Çizilmesi istenen eleman gruplarını içeren liste
                         ["col", "colSpan", "beam" ve "slab"]
        alpha          : En opak yapısal eleman sınıfının opaklık derecesi (0-1)
        zorder         : En üstteki yapısal eleman sınıfının çizim sırası
        hatchScale     : Kolonlar için tarama çizgisi ölçeği

    Returns:
        tuple: (fig, ax) matplotlib pencere ve çizim nesneleri

    Requires:
        os
        draw_basic_geometry as drawBasic
    """
    fig, ax = basic_geometry
    
    # Yapı elemanlarını çiz
    draw_member_groups(
        ax,
        data_struct, member_groups,
        alpha, zorder, hatchScale
    )
    
    # Çizim sonrası ayarlamaları yap
    drawBasic.make_finalCanvasAdjustments(ax)
    
    # geç, göster veya kaydet
    if action   == "none": pass
    elif action == "show": drawBasic.show_canvas()
    elif action == "save":
        script_path = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_path, fileName)
        fig.savefig(output_path, bbox_inches="tight", dpi=300)
    
    return fig, ax