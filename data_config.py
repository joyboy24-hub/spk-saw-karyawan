# data_config.py

# Data Karyawan (Sesuai PPT)
DATA_KARYAWAN = {
    "Alternatif": ["A1", "A2", "A3", "A4"],
    "Nama":       ["Budi", "Siti", "Bambang", "Dewi"],
    "C1_Disiplin":  [3, 1, 4, 2],       # Cost
    "C2_Target":    [85, 90, 75, 95],   # Benefit
    "C3_Kerjasama": [75, 80, 85, 70],   # Benefit
    "C4_Loyalitas": [3, 2, 5, 4],       # Benefit
}

# Kriteria dan Bobot
KRITERIA = [
    {"Kode": "C1", "Nama": "Kedisiplinan (Hari Terlambat)", "Sifat": "Cost",    "Bobot": 0.25},
    {"Kode": "C2", "Nama": "Pencapaian Target Kerja",       "Sifat": "Benefit", "Bobot": 0.35},
    {"Kode": "C3", "Nama": "Kerjasama Tim",                 "Sifat": "Benefit", "Bobot": 0.20},
    {"Kode": "C4", "Nama": "Loyalitas / Masa Kerja (Tahun)","Sifat": "Benefit", "Bobot": 0.20},
]