import numpy as np
"""
Required by:
    round_array
"""

import time
"""
Required by:
    measure_exec_time
"""

import copy
"""
Required by:
    apply_masks
"""





def round_array(arr, decimals: int = 4):
    """
    Verilen bir numpy dizisini belirtilen ondalık basamak sayısına yuvarlar.
    
    Args:
        arr (numpy.ndarray): Yuvarlanacak numpy dizisi.
        decimals (int): Yuvarlama için ondalık basamak sayısı.

    Returns:
        numpy.ndarray: Yuvarlanmış dizi.

    Requires:
        numpy
    """
    return np.round(arr, decimals)





def measure_exec_time(desc: str, func, *args, **kwargs):
    """
    Verilen fonksiyonun çalışma süresini ölçer ve ekrana yazdırır.

    Args:
        desc (str): Fonksiyonun ne yaptığını açıklayan bir metin.
        func (callable): Çalışma süresi ölçülecek fonksiyon.
        *args: Fonksiyona gönderilecek konumlu argümanlar.
        **kwargs: Fonksiyona gönderilecek anahtar kelime argümanları.
    
    Returns:
        Any: Fonksiyonun döndürdüğü değer.
    
    Requires:
        time
    """    
    start  = time.perf_counter()
    result = func(*args, **kwargs)
    end    = time.perf_counter()
    print(f"{desc} çalışma süresi: {end - start:.4f} s")
    return result





def apply_masks(cand, idx_list, mask_list, option_list):
    """
    cand listesinin (çözüm adayı) idx_list ile verilen bileşenlerine, mask_list ile verilen
    ve karşılık gelen maskeyi, option_list ile verilen yine karşılık gelen kurala göre uygular.

    Args:
        cand (list[np.ndarray])      : Çözümün tasarım vektörü (manual_design_vector.md dosyasına bakınız)
        idx_list (list[int])         : cand listesindeki ilgili bileşenlerin indeksleri
        mask_list (list[np.ndarray]) : cand[idx]'lere uygulanacak True/False maskeleri
        option_list (list[str])      : "True_is_0", "True_is_1", "True_is_0_else_1", "True_is_1_else_0"
            - "True_is_0"        : True elemanları 0 yap, diğerlerini değiştirme
            - "True_is_1"        : True elemanları 1 yap, diğerlerini değiştirme
            - "True_is_0_else_1" : True elemanları 0 yap, diğerlerini 1 yap
            - "True_is_1_else_0" : True elemanları 1 yap, diğerlerini 0 yap

    Returns:
        list: cand listesinin ilgili bileşenlerine maske uygulanmış yeni bir kopyası

    Requires:
        copy
    """
    cand_copy = copy.deepcopy(cand)

    for idx, mask, option in zip(idx_list, mask_list, option_list):
        target = cand_copy[idx].copy()
        
        if option == "True_is_0":
            target[mask]  = 0
        elif option == "True_is_1":
            target[mask]  = 1
        elif option == "True_is_0_else_1":
            target[mask]  = 0
            target[~mask] = 1
        elif option == "True_is_1_else_0":
            target[mask]  = 1
            target[~mask] = 0
        else:
            raise ValueError(f"Geçersiz option: {option}")
        
        cand_copy[idx] = target
    
    return cand_copy