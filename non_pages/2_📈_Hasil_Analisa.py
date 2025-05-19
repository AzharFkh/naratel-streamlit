import streamlit as st
import pandas as pd
import plotly.express as px  # untuk bikin pie chart yang kece
from tools import sidebar_ui, page_style

# ==================== SETUP ====================
st.set_page_config(page_title="Hasil Analisa Sentimen", layout="wide")
st.title("📊 Hasil Analisa Sentimen")
st.subheader("📄 Data Sentimen dari Halaman Sebelumnya")

sidebar_ui()
page_style()

# ==================== LOGIKA ====================
if "hasil_analisa" in st.session_state and "Kolom ditampilkan" in st.session_state:
    data_diolah = st.session_state["hasil_analisa"]
    kolom_ditampil = st.session_state["Kolom ditampilkan"]
    
    st.dataframe(data_diolah[kolom_ditampil])

    df = pd.DataFrame(data_diolah[kolom_ditampil])

    # ➡️ Dropdown untuk pilih Post URL
    st.subheader("📌 Pilih Post untuk Melihat Hasil Sentimen")
    daftar_post = df["Post URL"].unique().tolist()
    selected_post = st.selectbox("Pilih Post URL", options=["Semua Post"] + daftar_post)

    # ➡️ Filter data berdasarkan pilihan
    if selected_post == "Semua Post":
        df_filtered = df
    else:
        df_filtered = df[df["Post URL"] == selected_post]

    # ➡️ Menampilkan informasi jumlah sentimen (Positif, Negatif, Netral)
    st.subheader(f"➡️ Statistik Sentimen")
    st.write(f"Post URL : {selected_post}")
    if "Label Sentimen" in df_filtered.columns:
        # Hitung jumlah per sentimen
        jumlah_sentimen = df_filtered["Label Sentimen"].value_counts().reset_index()
        jumlah_sentimen.columns = ["Sentimen", "Jumlah"]

        # Menampilkan jumlah komentar untuk post URL yang dipilih
        st.write(f"Jumlah Komentar untuk Post URL : {df_filtered.shape[0]} komentar")

        # Menampilkan jumlah per sentimen (Positif, Negatif, Netral)
        c1, c2, c3 = st.columns(3)
        c1.metric("🙂 Positif", jumlah_sentimen[jumlah_sentimen["Sentimen"] == "Positif"]["Jumlah"].values[0] if "Positif" in jumlah_sentimen["Sentimen"].values else 0)
        c2.metric("😐 Netral", jumlah_sentimen[jumlah_sentimen["Sentimen"] == "Netral"]["Jumlah"].values[0] if "Netral" in jumlah_sentimen["Sentimen"].values else 0)
        c3.metric("🙁 Negatif", jumlah_sentimen[jumlah_sentimen["Sentimen"] == "Negatif"]["Jumlah"].values[0] if "Negatif" in jumlah_sentimen["Sentimen"].values else 0)

        st.divider()  # Divider antara informasi jumlah sentimen dan pie chart

        # ➡️ Pie Chart
        st.subheader(f"➡️ Distribusi Sentimen")
        fig = px.pie(
            jumlah_sentimen, 
            names="Sentimen", 
            values="Jumlah", 
            #title=f"Distribusi Sentimen {'(Semua Post)' if selected_post == 'Semua Post' else f'({selected_post})'}",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            height=600,  # tinggi chart
            width=600,   # lebar chart
        )

        st.plotly_chart(fig, use_container_width=True)

        # Simpan ke session_state kalau mau dipakai di halaman lain
        st.session_state["jumlah_label"] = jumlah_sentimen

        # ➡️ Dropdown untuk memilih label sentimen tertentu
        st.subheader("🔍 Tampilkan Komentar Berdasarkan Label Sentimen")

        opsi_label = jumlah_sentimen["Sentimen"].tolist()
        selected_sentimen = st.selectbox("Pilih Label Sentimen", options=opsi_label)

        # Filter dan tampilkan komentar sesuai label
        komentar_terfilter = df_filtered[df_filtered["Label Sentimen"] == selected_sentimen]

        st.write(f"Menampilkan {len(komentar_terfilter)} komentar dengan label: **{selected_sentimen}**")
        st.dataframe(komentar_terfilter[["Post URL", "Komentar", "Label Sentimen"]])



    else:
        st.warning("📌 Kolom 'Label Sentimen' tidak ditemukan di dataframe.")

else:
    st.warning("⚠️ Data Belum Dianalisis. Coba ke halaman Analisa Sentimen")
