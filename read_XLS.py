import pandas as pd
"""
Required by:
    read_XLS
"""





def sheet_to_dict(df):
    """
    Verilen pandas DataFrame nesnesini sözlüğe dönüştürür.

    Args:
        df (pd.DataFrame): Dönüştürülecek pandas DataFrame nesnesi
    
    Returns:
        dict: DataFrame'den oluşturulan sözlük

    Requires:
        None
    """
    result = {}
    for col in df.columns:
        values = df[col].to_numpy()
        if len(values) == 1  : result[col] = values[0]
        elif len(values) > 1 : result[col] = values
        else                 : result[col] = None
    return result





def read_XLS(file_name: str):
    """
    Verilen XLS (veya XLSX) dosyasını okur ve içindeki verileri sözlük olarak döndürür.

    Args:
        file_name (str): okunacak XLS dosyasının yolu
    
    Returns:
        dict: XLS dosyasından okunan verileri içeren sözlük

    Requires:
        pandas
        sheet_to_dict
    """
    xls = pd.read_excel(file_name, sheet_name=None)
    return {sheet: sheet_to_dict(df) for sheet, df in xls.items()}