import streamlit as st
from analisa_roberta import analyze_sentiment
from tools import sidebar_ui, page_style

# ==================== SETUP ====================
st.set_page_config(page_title="Analisis Sentimen Komentar Instagram", layout="wide")
st.title("📊 Analisis Sentimen Komentar Instagram")
st.subheader("📄 Data Scraping dari Halaman Sebelumnya")
sidebar_ui()
page_style()


# ==================== FUNGSI ====================
def tampilkan_hasil(df):
    """Fungsi untuk menampilkan hasil analisis"""
    st.subheader("➡️ Hasil Analisis Sentimen")
    st.dataframe(df[st.session_state["Kolom ditampilkan"]])

def proses_analisis(df):
    """Fungsi untuk menganalisis komentar dan menyimpan hasil ke session_state"""
    with st.spinner("🔎 Sedang menganalisis..."):
        result_df = analyze_sentiment(df, text_column="Komentar")
        
        # Simpan hasil ke session —> Hasil Analisis TERPISAH dari Data Scraping
        st.session_state["hasil_analisa"] = result_df.copy()  # <- copy() biar aman
        st.session_state["Kolom ditampilkan"] = ["Post URL", "Komentar", "Label Sentimen"]
        st.session_state["data_label"] = result_df["Label Sentimen"].value_counts()
        
        st.success("✅ Analisis selesai, periksa di halaman Hasil Analisa! 🎉")


# ==================== LOGIKA ====================

# 1️⃣ Cek jika ada hasil scraping
# Aman dari bencana modifikasi
if "data_scraping" in st.session_state:
    data_analisa = st.session_state["data_scraping"].copy()
    st.dataframe(data_analisa)

    if st.button("🚀 Mulai Analisis Data"):
        proses_analisis(data_analisa)

else:
    st.warning("⚠️ Belum ada data untuk dianalisis. Silakan scraping terlebih dahulu.")
