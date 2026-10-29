# saw_engine.py
import pandas as pd
import numpy as np

def hitung_saw(df, kriteria):
    """
    Fungsi untuk menghitung normalisasi dan skor akhir metode SAW.
    """
    bobot = np.array([k["Bobot"] for k in kriteria])
    sifat = [k["Sifat"] for k in kriteria]
    
    # Ambil kolom yang berawalan C (C1, C2, C3, C4)
    kolom_data = [c for c in df.columns if c.startswith("C")]
    
    matrix = df[kolom_data].astype(float).values
    R = np.zeros_like(matrix, dtype=float)

    # Proses Normalisasi
    for j, s in enumerate(sifat):
        col = matrix[:, j]
        if s == "Benefit":
            R[:, j] = col / col.max()
        else:  # Cost
            R[:, j] = col.min() / col

    # Hitung Skor & Ranking
    df_norm = pd.DataFrame(R, columns=[f"R_{c}" for c in kolom_data])
    skor = R @ bobot
    df_norm["Skor_Akhir"] = skor
    df_norm["Ranking"] = df_norm["Skor_Akhir"].rank(ascending=False, method="min").astype(int)
    
    return df_norm, R