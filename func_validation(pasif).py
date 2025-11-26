import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mcoll
from collections import Counter

"""
Required by:
    analyze_contBeam.py
"""

def validate_data_integrity(contBeam, contBeamTopo, geoData):
    """
    Sürekli kiriş verilerinin yapısal bütünlüğünü, vektör uyumunu ve geometrik doğruluğunu denetler.

    Bu fonksiyon şu kontrolleri yapar:
    1. Topoloji vektörü ile kiriş listesinin boyut uyumu.
    2. Topoloji değerlerinin geçerliliği (-1, 0, 1).
    3. Her bir kirişin düğümleri arasındaki geometrik bağlantıların (Node Connectivity) varlığı.

    Args:
        contBeam (list): Sürekli kiriş tanımlarını içeren sözlükler listesi.
                         Her öğe 'nodes' (düğüm indeksleri listesi) anahtarına sahip olmalıdır.
        contBeamTopo (np.ndarray): Kirişlerin durumunu belirten tamsayı vektörü.
                                   1: Aktif, 0: Pasif, -1: Geçersiz/Void.
        geoData (dict): Proje geometrik verileri (nodes, nodeDist vb.).

    Returns:
        dict: Analiz sonuçlarını, istatistikleri ve tespit edilen hataları içeren rapor sözlüğü.
              Anahtarlar: 'total_beams', 'connection_errors', 'stats', 'active_lengths' vb.
    """
    results = {
        "total_beams": len(contBeam),
        "topo_shape_match": False,
        "valid_topo_values": True,
        "connection_errors": [],
        "node_sequence_errors": [],
        "stats": {},
        "active_lengths": []
    }

    # 1. Vektör Boyutu Kontrolü
    if len(contBeamTopo) == len(contBeam):
        results["topo_shape_match"] = True
    else:
        print(f"HATA: contBeamTopo boyutu ({len(contBeamTopo)}) ile contBeam listesi ({len(contBeam)}) uyuşmuyor!")
        return results

    # 2. Topoloji Değer Kontrolü (-1, 0, 1 dışında değer var mı?)
    valid_values = {-1, 0, 1}
    unique_values = set(np.unique(contBeamTopo))
    if not unique_values.issubset(valid_values):
        results["valid_topo_values"] = False
        print(f"UYARI: Geçersiz topoloji değerleri tespit edildi: {unique_values - valid_values}")

    # İstatistikler
    counts = Counter(contBeamTopo)
    results["stats"] = {
        "Active (1)": counts.get(1, 0),
        "Passive (0)": counts.get(0, 0),
        "Void (-1)": counts.get(-1, 0)
    }

    # 3. Geometrik Bağlantı ve Süreklilik Kontrolü
    nodes = geoData["nodes"]
    nodeDist = geoData["nodeDist"]

    for idx, beam in enumerate(contBeam):
        beam_nodes = beam["nodes"]
        
        # a) Düğüm sırası kontrolü (Ardışık düğümler arasında bağlantı var mı?)
        path_length = 0
        is_valid_path = True
        
        for i in range(len(beam_nodes) - 1):
            n1, n2 = beam_nodes[i], beam_nodes[i+1]
            dist = nodeDist[n1, n2]
            
            if dist == -1: # Bağlantı yoksa
                results["connection_errors"].append(idx)
                is_valid_path = False
                break
            
            path_length += dist

        # Aktif kirişse uzunluğunu kaydet
        if contBeamTopo[idx] == 1 and is_valid_path:
            results["active_lengths"].append(path_length)
            
        # b) Kiriş parçası (span) eşleşmesi kontrolü
        # beam["beam"] içindeki span indeksleri ile geometrik spanlar örtüşüyor mu?
        # (Bu kısım daha derin analiz gerektirir, şimdilik path kontrolü yeterli)

    return results

def plot_topology_distribution(stats):
    """
    Sürekli kirişlerin durum dağılımını (Aktif/Pasif/Void) bar grafiği ile görselleştirir.

    Args:
        stats (dict): 'Active (1)', 'Passive (0)' ve 'Void (-1)' anahtarlarına sahip sayı sözlüğü.

    Returns:
        None: Grafiği ekrana basar (plt.show).
    """
    labels = list(stats.keys())
    values = list(stats.values())
    colors = ['green', 'gray', 'red'] # Active, Passive, Void

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values, color=colors, alpha=0.7, edgecolor='black')
    
    ax.set_title('Sürekli Kiriş Topoloji Dağılımı', fontsize=14)
    ax.set_ylabel('Adet')
    
    # Barların üzerine sayıları yaz
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=12)
    
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.show()

def plot_active_beam_lengths(lengths):
    """
    Sistemdeki aktif sürekli kirişlerin uzunluk dağılımını histogram olarak çizer.
    
    Bu grafik, tasarlanan kirişlerin genel uzunluk karakteristiğini anlamak için kullanılır.

    Args:
        lengths (list): Aktif kirişlerin uzunluk değerlerini içeren liste.

    Returns:
        None: Grafiği ekrana basar.
    """
    if not lengths:
        print("Histogram çizilecek aktif kiriş bulunamadı.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    n, bins, patches = ax.hist(lengths, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    
    ax.set_title('Aktif Sürekli Kiriş Uzunluk Dağılımı', fontsize=14)
    ax.set_xlabel('Uzunluk (birim)')
    ax.set_ylabel('Frekans')
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.show()

def visualize_beams_on_plan(geoData, contBeam, contBeamTopo, errors):
    """
    Sürekli kiriş hatlarını mimari plan üzerinde durumlarına göre renklendirerek çizer.

    Renk Kodları:
    - Yeşil (Kalın): Aktif Hatlar (1)
    - Gri (İnce, Saydam): Pasif Hatlar (0)
    - Kırmızı (Çok Kalın): Hatalı/Kopuk Hatlar

    Args:
        geoData (dict): Düğüm koordinatlarını içeren geometrik veri.
        contBeam (list): Kiriş tanımları.
        contBeamTopo (np.ndarray): Kiriş durum vektörü.
        errors (list): Hatalı olduğu tespit edilen kiriş indeksleri listesi.

    Returns:
        None: Matplotlib penceresi açar.
    """
    nodes = geoData["nodes"]
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_aspect('equal')
    ax.set_facecolor('#f9f9f9')
    ax.set_title("Sürekli Kiriş Analiz Planı", fontsize=16)

    # 1. Arkaplan: Akslar ve Düğümler (Silik)
    ax.scatter(nodes[:,0], nodes[:,1], c='black', s=10, alpha=0.3, zorder=1)
    
    # Çizim koleksiyonları
    active_lines = []
    passive_lines = []
    error_lines = []

    for idx, beam in enumerate(contBeam):
        path_nodes = nodes[beam["nodes"]]
        # Path koordinatlarını (N, 2) segmentlere ayır
        # LineCollection için segment formatı: [ [(x1,y1),(x2,y2)], ... ]
        # Sürekli hattı tek parça çizgi olarak ekliyoruz
        
        if idx in errors:
            error_lines.append(path_nodes)
        elif contBeamTopo[idx] == 1:
            active_lines.append(path_nodes)
        elif contBeamTopo[idx] == 0:
            passive_lines.append(path_nodes)
        # Void (-1) olanları çizmiyoruz (kalabalık yapmasın)

    # 2. Pasif Hatlar (Gri, İnce)
    if passive_lines:
        lc_passive = mcoll.LineCollection(passive_lines, colors='gray', linewidths=1, alpha=0.4, label='Pasif (0)')
        ax.add_collection(lc_passive)

    # 3. Aktif Hatlar (Yeşil, Orta)
    if active_lines:
        lc_active = mcoll.LineCollection(active_lines, colors='green', linewidths=2.5, alpha=0.8, label='Aktif (1)')
        ax.add_collection(lc_active)

    # 4. Hatalı Hatlar (Kırmızı, Kalın, Yanıp Sönen gibi)
    if error_lines:
        lc_error = mcoll.LineCollection(error_lines, colors='red', linewidths=4, alpha=1.0, label='Hatalı Bağlantı')
        ax.add_collection(lc_error)

    # Legend ve Ayarlar
    ax.legend(loc='upper right')
    ax.autoscale()
    
    # Eksen etiketlerini kaldır
    ax.set_xticks([])
    ax.set_yticks([])
    
    plt.tight_layout()
    plt.show()

def print_detailed_report(results):
    """
    Analiz sonuçlarını okunabilir, formatlı bir metin raporu olarak konsola basar.

    Args:
        results (dict): 'validate_data_integrity' fonksiyonundan dönen sonuç sözlüğü.

    Returns:
        None
    """
    total = results["total_beams"]
    stats = results["stats"]
    
    print("\n" + "="*50)
    print(f"{'SÜREKLİ KİRİŞ DOĞRULAMA RAPORU':^50}")
    print("="*50)
    
    print(f"\nGENEL BAKIŞ:")
    print(f"  • Toplam Tanımlı Hat Sayısı : {total}")
    print(f"  • Vektör Boyutu Eşleşmesi   : {'✅ BAŞARILI' if results['topo_shape_match'] else '❌ BAŞARISIZ'}")
    print(f"  • Veri Değer Bütünlüğü      : {'✅ GEÇERLİ' if results['valid_topo_values'] else '❌ GEÇERSİZ DEĞERLER'}")

    print(f"\nDAĞILIM:")
    print(f"  • Aktif (Seçili) Hatlar     : {stats['Active (1)']:>4} (%{stats['Active (1)']/total*100:.1f})")
    print(f"  • Pasif (Yedek) Hatlar      : {stats['Passive (0)']:>4} (%{stats['Passive (0)']/total*100:.1f})")
    print(f"  • Yasaklı/Void Hatlar       : {stats['Void (-1)']:>4} (%{stats['Void (-1)']/total*100:.1f})")

    print(f"\nHATA ANALİZİ:")
    err_count = len(results["connection_errors"])
    if err_count == 0:
        print("  ✅ Hiçbir bağlantı kopukluğu tespit edilmedi.")
    else:
        print(f"  ❌ {err_count} adet hatta kopukluk veya geçersiz düğüm tespit edildi.")
        print(f"  • Hatalı Hat İndeksleri: {results['connection_errors'][:10]} {'...' if err_count > 10 else ''}")

    print(f"\nMETRİKLER:")
    print(f"  • Veri Sağlamlık Oranı      : %{(1 - err_count/total)*100:.2f}")
    if results["active_lengths"]:
        print(f"  • Ort. Aktif Kiriş Uzunluğu : {np.mean(results['active_lengths']):.2f} birim")
        print(f"  • Max. Aktif Kiriş Uzunluğu : {np.max(results['active_lengths']):.2f} birim")
    
    print("="*50 + "\n")