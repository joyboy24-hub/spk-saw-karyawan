# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Import dari file lokal yang kita buat
from data_config import DATA_KARYAWAN, KRITERIA
from saw_engine import hitung_saw

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="SPK SAW - Pemilihan Karyawan Terbaik",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2.2rem; }
    .main-header p { margin: 0.5rem 0 0; opacity: 0.9; }
    .winner-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #f59e0b;
        text-align: center;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER UTAMA
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🏆 Sistem Pendukung Keputusan</h1>
    <p>Metode Simple Additive Weighting (SAW) — Pemilihan Karyawan Terbaik</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR: PENGATURAN BOBOT & DATA
# ============================================================
with st.sidebar:
    st.header("⚙️ Pengaturan Bobot Kriteria")
    st.caption("Geser slider untuk simulasi. Total bobot harus = 1.00")

    bobot_input = []
    for k in KRITERIA:
        val = st.slider(
            f"{k['Kode']} — {k['Nama']}",
            min_value=0.0, max_value=1.0,
            value=k["Bobot"], step=0.05,
            help=f"Sifat: {k['Sifat']}"
        )
        bobot_input.append(val)

    total_bobot = sum(bobot_input)
    if abs(total_bobot - 1.0) < 0.001:
        st.success(f"✅ Total bobot: {total_bobot:.2f}")
    else:
        st.warning(f"⚠️ Total bobot: {total_bobot:.2f} (harus 1.00)")

    st.divider()
    st.subheader("📋 Edit Data Alternatif")
    st.caption("Ubah nilai untuk melihat perubahan hasil secara langsung.")
    
    df_editor = pd.DataFrame(DATA_KARYAWAN).set_index("Alternatif")[["Nama","C1_Disiplin","C2_Target","C3_Kerjasama","C4_Loyalitas"]]
    data_edit = st.data_editor(df_editor, use_container_width=True, num_rows="fixed")

# Update bobot kriteria berdasarkan slider
kriteria_updated = []
for k, b in zip(KRITERIA, bobot_input):
    kk = k.copy()
    kk["Bobot"] = b
    kriteria_updated.append(kk)

# ============================================================
# PROSES PERHITUNGAN SAW (Panggil fungsi dari saw_engine.py)
# ============================================================
df = data_edit.reset_index().copy()
df_norm, R = hitung_saw(df, kriteria_updated)
kolom_data = [c for c in df.columns if c.startswith("C")]

hasil = df[["Alternatif","Nama"]].copy()
hasil["Skor_Akhir"] = df_norm["Skor_Akhir"].round(4)
hasil["Ranking"] = df_norm["Ranking"]
hasil = hasil.sort_values("Ranking").reset_index(drop=True)

# ============================================================
# TAB NAVIGASI
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "📋 Data & Normalisasi", "🏆 Hasil & Ranking", "📖 Tentang SAW"]
)

# ------------------------------------------------------------
# TAB 1: DASHBOARD
# ------------------------------------------------------------
with tab1:
    winner = hasil.iloc[0]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Kandidat", len(hasil))
    c2.metric("📌 Jumlah Kriteria", len(kriteria_updated))
    c3.metric("🏅 Nilai Tertinggi", f"{winner['Skor_Akhir']:.4f}")
    c4.metric("🎖️ Karyawan Terbaik", winner["Nama"])

    st.divider()

    st.markdown(f"""
    <div class="winner-card">
        <h2>🏆 Karyawan Terbaik</h2>
        <h1 style="color:#b45309; margin:0.3rem 0;">{winner['Nama']} ({winner['Alternatif']})</h1>
        <p style="font-size:1.1rem; margin:0;">
            Nilai Preferensi: <b>{winner['Skor_Akhir']:.4f}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📊 Nilai Preferensi Setiap Alternatif")
        fig_bar = px.bar(
            hasil, x="Nama", y="Skor_Akhir", color="Skor_Akhir",
            color_continuous_scale="Blues", text="Skor_Akhir"
        )
        fig_bar.update_traces(texttemplate="%{text:.4f}", textposition="outside")
        fig_bar.update_layout(
            yaxis_range=[0, hasil["Skor_Akhir"].max() * 1.15],
            xaxis_title="Kandidat", yaxis_title="Nilai V",
            coloraxis_showscale=False, height=400
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("🎯 Komposisi Bobot Kriteria")
        labels = [f"{k['Kode']}\n{k['Bobot']*100:.0f}%" for k in kriteria_updated]
        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=[k["Bobot"] for k in kriteria_updated],
            hole=0.5,
            marker=dict(colors=["#3b82f6","#10b981","#f59e0b","#ef4444"]),
            textinfo="label"
        )])
        fig_pie.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("🕸️ Perbandingan Profil Alternatif (Normalisasi)")
    fig_radar = go.Figure()
    for i, row in df_norm.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=R[i].tolist() + [R[i][0]],
            theta=[k["Kode"] for k in kriteria_updated] + [kriteria_updated[0]["Kode"]],
            fill="toself", name=df["Nama"].iloc[i]
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        height=450, showlegend=True
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ------------------------------------------------------------
# TAB 2: DATA & NORMALISASI
# ------------------------------------------------------------
with tab2:
    st.subheader("1️⃣ Matriks Keputusan Awal (Data Mentah)")
    st.dataframe(df[["Alternatif","Nama"] + kolom_data], use_container_width=True)

    st.subheader("2️⃣ Matriks Normalisasi (R)")
    st.caption("Cost: r = min/x  |  Benefit: r = x/max")
    norm_show = df_norm[[f"R_{c}" for c in kolom_data]].copy()
    norm_show.insert(0, "Alternatif", df["Alternatif"])
    norm_show.insert(1, "Nama", df["Nama"])
    st.dataframe(norm_show.round(4), use_container_width=True)

    st.subheader("3️⃣ Matriks Terbobot (R × W)")
    bobot_arr = np.array([k["Bobot"] for k in kriteria_updated])
    R_bobot = R * bobot_arr
    df_rb = pd.DataFrame(R_bobot, columns=[f"W×{c}" for c in kolom_data])
    df_rb.insert(0, "Nama", df["Nama"])
    df_rb["Total (V)"] = R_bobot.sum(axis=1).round(4)
    st.dataframe(df_rb.round(4), use_container_width=True)

    st.subheader("4️⃣ Tabel Kriteria & Bobot")
    st.dataframe(pd.DataFrame(kriteria_updated), use_container_width=True)

# ------------------------------------------------------------
# TAB 3: HASIL & RANKING
# ------------------------------------------------------------
with tab3:
    st.subheader("🏆 Peringkat Akhir Kandidat")

    hasil_display = hasil.copy()
    medals = ["🥇","🥈","🥉","🏅"]
    hasil_display["Medali"] = [medals[i] if i < len(medals) else "🏅" for i in range(len(hasil_display))]
    hasil_display = hasil_display[["Ranking","Medali","Alternatif","Nama","Skor_Akhir"]]
    
    st.dataframe(
        hasil_display.style.highlight_max(subset=["Skor_Akhir"], color="#bbf7d0"),
        use_container_width=True, hide_index=True
    )

    fig_rank = px.bar(
        hasil, x="Skor_Akhir", y="Nama", orientation="h",
        color="Skor_Akhir", color_continuous_scale="Viridis",
        text="Skor_Akhir"
    )
    fig_rank.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig_rank.update_layout(
        xaxis_range=[0, hasil["Skor_Akhir"].max() * 1.2],
        xaxis_title="Nilai Preferensi (V)", yaxis_title="Kandidat",
        coloraxis_showscale=False, height=400
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    st.success(
        f"✅ Berdasarkan perhitungan SAW, **{winner['Nama']} ({winner['Alternatif']})** "
        f"memperoleh nilai preferensi tertinggi sebesar **{winner['Skor_Akhir']:.4f}** "
        f"dan terpilih sebagai **Karyawan Terbaik**."
    )

    csv = hasil.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Hasil (CSV)",
        data=csv, file_name="hasil_saw_karyawan.csv",
        mime="text/csv"
    )

# ------------------------------------------------------------
# TAB 4: TENTANG SAW
# ------------------------------------------------------------
with tab4:
    st.subheader("📖 Apa itu Metode SAW?")
    st.markdown(r"""
    **Simple Additive Weighting (SAW)** atau metode penjumlahan terbobot adalah salah satu
    metode Multi-Attribute Decision Making (MADM) yang paling populer. Konsep dasarnya
    adalah mencari **penjumlahan terbobot** dari rating kinerja setiap alternatif pada semua kriteria.

    ### 🧮 Langkah-langkah:
    1. **Menentukan Alternatif (Ai)** — kandidat yang akan dipilih.
    2. **Menentukan Kriteria (Cj)** — beserta sifatnya (*Benefit* / *Cost*).
    3. **Menentukan Bobot Kepentingan (Wj)** — total $\sum W_j = 1$.
    4. **Membuat Matriks Keputusan (X)** — nilai tiap alternatif di tiap kriteria.
    5. **Normalisasi Matriks (R)**:
       - **Benefit:** $r_{ij} = \frac{x_{ij}}{\max(x_{ij})}$
       - **Cost:** $r_{ij} = \frac{\min(x_{ij})}{x_{ij}}$
    6. **Menghitung Nilai Preferensi (Vi):**
       $$V_i = \sum_{j=1}^{n} (w_j \cdot r_{ij})$$
    7. **Perankingan** — alternatif dengan **Vi tertinggi** adalah pilihan terbaik.
    """)

    st.info("💡 **Tips:** Ubah bobot di sidebar untuk melihat bagaimana peringkat berubah secara dinamis.")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown(
    "<p style='text-align:center; color:#64748b;'>"
    "SPK Metode SAW — Kelompok 1 | Aditya Erza Farandi · M. Aditya Syahidan · Doni Permana"
    "</p>",
    unsafe_allow_html=True
)