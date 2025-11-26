import numpy as np
"""
Required by:
    find_jumps
    find_transitions
    dfs_all_paths
    build_path_details
"""





def find_jumps(axNod, axesDirection, nodMat, spanLen, maxJumpLength=np.inf):
    """
    axNod listesi ile sıralı düğümleri verilen akslar arasındaki uygun geçişleri bulur.
    Bir aks ile ancak ikinci bir diğer aks arasında geçişler yapılabilir.

    Args:
        axNod (list of np.arrays)       : Eksenler üzerindeki düğümlerin indeksleri
        axesDirection (np.ndarray)      : Aksların birbirlerine göre yön bilgisi
        nodMat (np.ndarray)             : Düğümler arasındaki aks parçasının indeksini
                                          tutan matris
        spanLen (np.ndarray)            : Aks parçalarının (span) uzunlukları
        maxJumpLength (float, optional) : Maksimum geçiş uzunluğu
    
    Returns:
        list of np.arrays               : Akslar arasındaki geçişlerin listesi
    
    Requires:
        numpy
    """
    jumps = [[-1 for _ in range(len(axNod))] for _ in range(len(axNod))]

    for m, axis_m in enumerate(axNod):
        for n, axis_n in enumerate(axNod):
            # Eğer aynı aks ise atla
            if m == n                   : continue
            # Eğer aksların birbirlerine göre yönü belirli değilse atla
            if axesDirection[m][n] == 0 : continue

            jumps_for_mn = []
            
            for i, node_i in enumerate(axis_m):
                # İlk ve son düğümlerden diğer akslara geçiş yapılamaz
                if i == 0 or i == len(axis_m) - 1 : continue
                
                for j, node_j in enumerate(axis_n):
                    # İlk ve son düğümlerden diğer akslara geçiş yapılamaz
                    if j == 0 or j == len(axis_n) - 1       : continue
                    # Eğer düğümler aynı aks üzerinde ise atla
                    if node_j in axis_m or node_i in axis_n : continue
                    
                    span_id = nodMat[node_i][node_j]
                    
                    # Eğer iki düğüm arasında bir span varsa ve bu span uzunluğu
                    # maxJumpLength'ten küçükse geçiş ekle
                    if span_id != -1 and spanLen[span_id] <= maxJumpLength:
                        jumps_for_mn.append([node_i, node_j])
                        jumps_for_mn.append([node_j, node_i])
            
            # Eğer akslar arasında geçiş varsa, bu geçişleri kaydet
            if jumps_for_mn: jumps[m][n] = np.array(jumps_for_mn)
    
    return jumps





def find_transitions(axNod, axesDirection, jumps):
    """
    axNod listesi ile sıralı düğümleri verilen akslar arasındaki geçiş yapılabilecek
    aks çiftlerini bularak her aks için olası ardışık düğüm geçişlerini ve akslar arası
    geçişleri bir listede birleştirir.

    Args:
        axNod (list of np.arrays)       : Eksenler üzerindeki düğümlerin indeksleri
        axesDirection (np.ndarray)      : Aksların birbirlerine göre yön bilgisi
        jumps (list of np.arrays)       : Akslar arasındaki olası geçişlerin listesi
    
    Returns:
        list of np.arrays               : Akslar arasındaki geçişlerin listesi
    
    Requires:
        numpy
    """
    all_transitions = [[-1 for _ in range(len(axNod))] for _ in range(len(axNod))]
    all_start_nodes = [[-1 for _ in range(len(axNod))] for _ in range(len(axNod))]
    all_end_nodes   = [[-1 for _ in range(len(axNod))] for _ in range(len(axNod))]
    
    for m, nodes_m in enumerate(axNod):
        for n, nodes_n in enumerate(axNod):
            # Eğer m ve n aksları arasında geçiş yapılamaz ise atla
            if isinstance(jumps[m][n], int) and jumps[m][n] == -1 : continue

            # 1. İlk aksın ardışık düğüm geçişlerini bul
            on_axis_m = []
            for a, b in zip(nodes_m[:-1], nodes_m[1:]):
                on_axis_m.append([a, b])
            
            # 2. İkinci aks ters yöndeyse düğüm sırasını çevir
            if axesDirection[m][n] == -1 : nodes_n_ordered = nodes_n[::-1]
            else                         : nodes_n_ordered = nodes_n

            # 3. İkinci aksın ardışık düğüm geçişlerini bul
            on_axis_n = []
            for a, b in zip(nodes_n_ordered[:-1], nodes_n_ordered[1:]):
                on_axis_n.append([a, b])

            # 4. Akslar arası geçişleri, başlan ve bitiş düğümlerini kaydet
            all_transitions[m][n] = np.vstack((on_axis_m, on_axis_n, jumps[m][n]))
            all_start_nodes[m][n] = nodes_m[0]
            all_end_nodes[m][n]   = np.array([nodes_m[-1], nodes_n_ordered[-1]])

    return all_transitions, all_start_nodes, all_end_nodes





def dfs_all_paths(transitions, start_node, end_nodes):
    """
    Depth-First Search (DFS) algoritması ile verilen bir başlangıç düğümünden
    (start_node) verilen bitiş düğümlerine (end_nodes) kadar olan tüm yolları bulur.
    Bu yollar, transitions dizisinde verilen geçişler ile oluşturulur.

    Args:
        transitions (numpy.ndarray) : Olası geçişlerin listesi
        start_node (int)            : Başlangıç düğümü
        end_nodes (numpy.ndarray)   : Olası bitiş düğümleri
    
    Returns:
        list of numpy.ndarrays : Başlangıç düğümünden bitiş düğümlerine kadar olan
                                 tüm yolları içeren numpy dizileri listesi
    
    Requires:
        numpy
    """

    # Geçiş dizisini sözlüğe çevirerek yönlendirilmiş bir grafik oluştur
    graph = {}
    for src, dst in transitions:
        if src not in graph: graph[src] = []
        graph[src].append(dst)
    
    # Bulunan yolları saklamak için bir liste
    all_paths = []

    # DFS fonksiyonu
    def dfs(node, path):
        if node in path: return

        path.append(node)

        if node in end_nodes:
            all_paths.append(path.copy())
            path.pop()
            return

        for neighbor in graph.get(node, []):
            dfs(neighbor, path)

        path.pop()

    # Başlangıç düğümünden DFS başlat
    dfs(start_node, [])

    # Tüm yolları numpy dizilerine çevir ve döndür
    return [np.array(p) for p in all_paths]





def build_path_details(axNod, nodMat, all_transitions, all_start_nodes, all_end_nodes, jumps, maxJumpCount=2):
    """
    axNod listesinde verilen akslardan seçilen ikili kombinasyonlar kullanılarak oluşturulabilecek
    tüm ek yolların detaylarını çıkarır.

    Args:
        axNod (list of np.arrays)           : Eksenler üzerindeki düğümlerin indeksleri
        nodMat (np.array)                   : Düğümler arasındaki aks parçasının indeksini tutan matris
        all_transitions (list of np.arrays) : İlerleme ve geçiş için tüm düğüm çiftleri
        all_start_nodes (list of np.arrays) : Olası yolların başlangıç düğümleri
        all_end_nodes (list of np.arrays)   : Olası yolların bitiş düğümleri
        jumps (list of np.arrays)           : Akslar arası geçiş sağlayabilecek düğüm çiftleri
        maxJumpCount (int)                  : İki aks arasında izin verilen en fazla geçiş sayısı
    
    Returns:
        list of dict of np.arrays           : Aks çiftleri arasında bulunan tüm yolların detayları
    
    Requires:
        numpy
        dfs_all_paths
    """
    all_path_details = [[-1 for _ in range(len(axNod))] for _ in range(len(axNod))]

    for m, nodes_m in enumerate(axNod):
        for n, nodes_n in enumerate(axNod):
            
            # Eğer m ve n aksları arasında geçiş yapılamaz ise atla
            if isinstance(all_transitions[m][n], int) and all_transitions[m][n] == -1: continue
            
            # İki aks arasında yapılabilecek geçiş sayısı k ise, geçiş kullanılarak üretilebilecek
            # ek yolların sayısı 2^k - 1'dir. Bu ek yolların her biri ilk aksın başlangıç düğümünden
            # başlar ve ilk veya ikinci aksın bitiş düğümüne kadar devam eder.
            paths = dfs_all_paths(all_transitions[m][n], all_start_nodes[m][n], all_end_nodes[m][n])
            
            # Eğer iki aks kullanılarak bulunan bir yol üzerinde bulunan tüm düğümler, akslardan birine
            # ait ise bu yolu listeden çıkar; bu yol geçiş kullanmadan da üretilebilir.
            filtered_paths = [
                path for path in paths
                if not (np.all(np.isin(path, nodes_m)) or np.all(np.isin(path, nodes_n)))
            ]

            # İki aks arasında bulunan tüm yolların detaylarını çıkar ve sakla.
            path_details = []
            
            for path in filtered_paths:
                # Tüm hareketler (düğüm çiftleri şeklinde)
                path_transitions = np.column_stack((path[:-1], path[1:]))
            
                # Aynı aks üzerinde ve akslar arası geçişler ile yapılan hareketleri ayır
                same_axis, jump_axis = [], []
                for node_pair in path_transitions:
                    if any(np.array_equal(node_pair, j) for j in jumps[m][n]) : jump_axis.append(node_pair)
                    else                                                      : same_axis.append(node_pair)
                
                # Eğer akslar arası geçiş sayısı maxJumpCount'tan fazla ise bu yolu atla
                if len(jump_axis) > maxJumpCount : continue

                same_axis, jump_axis = np.array(same_axis), np.array(jump_axis)
                same_axis_spans = nodMat[same_axis[:, 0], same_axis[:, 1]]
                jump_axis_spans = nodMat[jump_axis[:, 0], jump_axis[:, 1]]

                # path_details listesine ilgili yolun detaylarını içeren bir sözlük ekle
                path_details.append({
                    "path"             : path,
                    "path transitions" : path_transitions,
                    "same axis"        : same_axis,
                    "jump axis"        : jump_axis,
                    "same axis spans"  : same_axis_spans,
                    "jump axis spans"  : jump_axis_spans
                })
            
            # Eğer iki aks arasında geçiş kullanılarak üretilebilecek yollar varsa, bu yolları sakla
            if path_details: all_path_details[m][n] = path_details

    return all_path_details





def build_data_cont_lines(axNod, axesDirection, nodMat, spanLen, maxJumpLength=np.inf, maxJumpCount=2):
    """
    axNod listesinde verilen akslardan seçilen ikili kombinasyonlar kullanılarak oluşturulabilecek
    tüm ek yolların detaylarını döner.

    Args:
        axNod (list of np.arrays)       : Eksenler üzerindeki düğümlerin indeksleri
        axesDirection (np.ndarray)      : Aksların birbirlerine göre yön bilgisi
        nodMat (np.array)               : Düğümler arasındaki aks parçasının indeksini tutan matris
        spanLen (np.ndarray)            : Aks parçalarının (span) uzunlukları
        maxJumpLength (float, optional) : Maksimum geçiş uzunluğu
        maxJumpCount (int)              : İki aks arasında izin verilen en fazla geçiş sayısı
    
    Returns:
        list of dict of np.arrays       : Aks çiftleri arasında bulunan tüm yolların detayları
    
    Requires:
        None
    """
    jumps = find_jumps(axNod, axesDirection, nodMat, spanLen, maxJumpLength)
    all_transitions, all_start_nodes, all_end_nodes = find_transitions(axNod, axesDirection, jumps)
    all_path_details = build_path_details(axNod, nodMat, all_transitions, all_start_nodes, all_end_nodes, jumps, maxJumpCount)
    return all_path_details