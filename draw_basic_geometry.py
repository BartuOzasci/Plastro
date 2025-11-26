import matplotlib.pyplot as plt
"""
Required by:
    draw_init_canvas
    show_canvas
"""

import matplotlib.collections as mcoll
"""
Required by:
    draw_axes
    draw_spans
    draw_areas
"""

import numpy as np
"""
Required by:
    draw_spans
"""

import os
"""
Required by:
    draw_basic_geometry
"""





def draw_init_canvas(figsize=(10, 6), dpi=100, facecolor="#f0f0f0"):
    """
    Matplotlib canvas'ını başlatır.
        
    Args:
        figsize   : Pencere boyutu (genişlik, yükseklik) inç cinsinden
        dpi       : Çözünürlük (inç başına nokta sayısı)
        facecolor : Çizim alanı arkaplan rengi (HEX veya isim)
    
    Returns:
        tuple: (fig, ax) matplotlib pencere ve çizim nesneleri
    
    Requires:
        matplotlib.pyplot as plt
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    ax.clear() # Önceki çizim kalıntılarını temizle
    ax.set_facecolor(facecolor) # Çizim alanı arkaplan rengini ayarla
    ax.set_aspect("equal") # Eksenleri eşit ölçeklendir
    ax.margins(x=0.02, y=0.02) # Kenar boşluklarını ayarla

    ax.set_xticks([]) # X ekseni işaretlerini kaldır
    ax.set_yticks([]) # Y ekseni işaretlerini kaldır

    # Çizim başlığı
    ax.set_title("plastro", fontdict={"family": "sans-serif", "size": 16, "weight": "bold"})

    return fig, ax





def draw_axes(ax, axes, color="black", linestyle="-.", linewidth=0.8, alpha=1):
    """
    Aks çizgilerini çizer.
    
    Args:
        ax: Matplotlib çizim ekseni nesnesi
        axes: Aks çizgilerini içeren numpy dizisi
        color (str): Çizgi rengi
        linestyle (str): Çizgi stili
        linewidth (float): Çizgi kalınlığı
        alpha (float): Çizgi şeffaflığı (0-1 arası)
    
    Returns:
        None
    
    Requires:
        matplotlib.collections as mcoll
    """

    # LineCollection ile çiz
    ax.add_collection(mcoll.LineCollection(
        axes,
        colors     = color,
        linestyles = linestyle,
        linewidths = linewidth,
        alpha      = alpha,
        zorder     = 5
    ))





def draw_nodes(ax, nodes, color="black", marker="x", size=6, alpha=1):
    """
    Düğüm noktalarını yüksek performansla çizer.
    
    Args:
        ax    : Matplotlib eksen nesnesi
        nodes : Düğüm koordinatları (N,2) np dizisi
        color : Düğüm rengi
        marker: Düğüm işaretleyici stili (örn. 'o', 'x', '^')
        size  : İşaretçi boyutu
        alpha : Şeffaflık (0-1)
    
    Returns:
        None
    
    Requires:
        None    
    """
    # Tüm düğümleri tek seferde çiz (vektörel işlem)
    ax.scatter(nodes[:,0], nodes[:,1], c=color, s=size**2, alpha=alpha, marker=marker, zorder=10)





def draw_labels(ax, nodes, color="blue", fontsize=7, offset=(0,0)):
    """
    Düğüm indekslerini yüksek performansla çizer (büyük veri setleri için optimize).
    
    Args:
        ax: Matplotlib eksen nesnesi
        nodes: Düğüm koordinatları (N,2) np dizisi
        color: Yazı rengi
        fontsize: Yazı boyutu
        offset: Yazı konumunu ayarlamak için (dx, dy) tuple'ı
    
    Returns:
        None
    
    Requires:
        None
    """

    dx, dy = offset
    
    for i, (x, y) in enumerate(nodes):
        ax.text(
            x + dx, y + dy,
            str(i),
            fontsize = fontsize,
            color    = color,
            ha       = "center",
            va       = "center",
            zorder   = 15,
            
            bbox = dict(
                facecolor = "white",          # Arka plan rengi
                alpha     = 0.7,              # Saydamlık (0: tamamen saydam, 1: opak)
                edgecolor = "none",           # Kenarlık rengi
                boxstyle  = "round, pad=0.05" # Kutunun şekli ve iç boşluğu
            )
        )

        ax.update_datalim([(x, y)]) # metin koordinatını çizim sınırlarına ekle





def draw_spans(ax, spans, nodes, color='red', linestyle="-", linewidth=2, alpha=1):
    """
    Aks parçalarını çizer.
    
    Args:
        ax        : Matplotlib eksen nesnesi
        spans     : Aks parçalarını içeren numpy dizisi (N,2) şeklinde düğüm indeksleri
        nodes     : Düğüm koordinatları (N,2) np dizisi
        color     : Çizgi rengi
        linestyle : Çizgi stili
        linewidth : Çizgi kalınlığı
        alpha     : Şeffaflık (0-1 arası)
    
    Returns:
        None
    
    Requires:
        matplotlib.collections as mcoll
        numpy as np
    """
    # Aks parçalarının başlangıç ve bitiş noktaları
    starts, ends = nodes[spans[:, 0]], nodes[spans[:, 1]]

    ax.add_collection(mcoll.LineCollection(
        np.stack([starts, ends], axis=1),
        colors     = color,
        linestyles = linestyle,
        linewidths = linewidth,
        capstyle   = "round",
        alpha      = alpha,
        zorder     = 8
    ))





def draw_areas(ax, areas, nodes, color="blue", linestyle="-", linewidth=2, alpha=0.5):
    """
    Alanları çizer.
    
    Args:
        ax        : Matplotlib eksen nesnesi
        areas     : Alan düğüm indeks listeleri
        nodes     : Düğüm koordinatları (N,2) np dizisi
        color     : Çizgi rengi
        linestyle : Çizgi stili
        linewidth : Çizgi kalınlığı
        alpha     : Şeffaflık

    Returns:
        None
    
    Requires:
        matplotlib.collections as mcoll
    """
    # Alanları hazırla
    polygons = [nodes[area] for area in areas]

    # Saydam dolgulu PolyCollection
    ax.add_collection(mcoll.PolyCollection(
        polygons,
        facecolors = color,     # Arka plan rengi
        edgecolors = "none",    # Kenarlık rengi
        linestyles = linestyle, # Kenarlık stili
        linewidths = linewidth, # Kenarlık kalınlığı
        alpha      = alpha,     # Şeffaflık (0-1 arası)
        zorder     = 7          # Çizim sırası
    ))





def make_finalCanvasAdjustments(ax):
    """
    Matplotlib canvas'ının son ayarlarını yapar.

    Args:
        ax: Matplotlib eksen nesnesi
    
    Returns:
        None
    
    Requires:
        None
    """
    ax.autoscale_view() # Görünümü otomatik ölçeklendir (aspect ratio'yu koruyarak)

    xMin, xMax = ax.get_xlim()
    yMin, yMax = ax.get_ylim()
    Lx, Ly     = xMax - xMin, yMax - yMin

    # Eksen başlıklarına yazdır
    ax.set_xlabel(f"L$_x$ : {int(Lx)} cm ({Lx/100:.1f} m)", fontdict={'family': 'sans-serif', 'size': 12})
    ax.set_ylabel(f"L$_y$ : {int(Ly)} cm ({Ly/100:.1f} m)", fontdict={'family': 'sans-serif', 'size': 12})





def show_canvas():
    """
    Matplotlib canvas'ını gösterir.

    Args:
        None
    
    Returns:
        None
    
    Requires:
        matplotlib.pyplot as plt
    """
    plt.show()





#! basePol ve floorPol çizdirme özellikleri de eklenmeli
#! alwaysBeam, neverBeam, ... çizdirme özellikleri de eklenmeli
def draw_basic_geometry(
        axes, nodes, spans, areas, spansG, areasG,
        action = "none",
        fileName = "_output.png",
        components = ["axes", "nodes", "spans", "areas", "axis labels", "node labels", "span labels", "area labels"]
    ):
    """
    Temel geometri çizimini yapar.

    Args:
        axes       : Aks çizgileri (N,2) numpy dizisi
        nodes      : Düğüm koordinatları (N,2) numpy dizisi
        spans      : Aks parçaları düğüm indeksleri için (M,2) numpy dizisi
        areas      : Alan düğüm indeks listeleri
        spansG     : Aks parçalarının orta noktaları (M,2) numpy dizisi
        areasG     : Alanların geometrik merkezleri (K,2) numpy dizisi
        action     : "none", "show" veya "save" olarak belirlenir
        fileName   : Çıktı dosya adı (sadece "save" için geçerli)
        components : Çizilecek bileşenlerin listesi
    
    Returns:
        tuple: (fig, ax) matplotlib pencere ve çizim nesneleri
    
    Requires:
        os
    """
    fig, ax = draw_init_canvas()
    
    if "axes" in components  : draw_axes(ax, axes)
    if "nodes" in components : draw_nodes(ax, nodes)
    if "spans" in components : draw_spans(ax, spans, nodes)
    if "areas" in components : draw_areas(ax, areas, nodes)
    
    if "axis labels" in components:
        draw_labels(ax, axes[:,0], "black", 10)
        draw_labels(ax, axes[:,1], "black", 10)
    
    if "node labels" in components : draw_labels(ax, nodes, "blue", 7)
    if "span labels" in components : draw_labels(ax, spansG, "red")
    if "area labels" in components : draw_labels(ax, areasG, "green", 10)

    make_finalCanvasAdjustments(ax)
    
    if action   == "none": pass
    elif action == "show": show_canvas()
    elif action == "save":
        script_path = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_path, fileName)
        fig.savefig(output_path, bbox_inches="tight", dpi=300)
    
    return fig, ax