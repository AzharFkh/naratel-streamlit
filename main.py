import streamlit as st
from scraper import create_driver, login_instagram, alat_scraper
from analisa_roberta import analyze_sentiment
from tools import sidebar_ui, page_style, navbar_style
import plotly.express as px
import pandas as pd
import tempfile
from streamlit_navigation_bar import st_navbar


current_page = navbar_style()

sidebar_ui()
page_style()

# Judul utama
st.title("Sentimen Analisis Sosial Media Kapten Naratel")

# Simulasi halaman 1: Upload & scraping
if current_page == "Upload & Scrape":
   with st.form(key='login_form'):
    st.subheader("🔑 Login Instagram")
    USERNAME = st.text_input("Username Instagram", type="default")
    PASSWORD = st.text_input("Password Instagram", type="password")
    submit_button = st.form_submit_button("Login")

    if submit_button:
        if USERNAME and PASSWORD:
            st.session_state["USERNAME"] = USERNAME
            st.session_state["PASSWORD"] = PASSWORD
            st.success("✅ Login berhasil! Username dan password disimpan.")
        else:
            st.error("⚠️ Username dan Password harus diisi!")

    st.divider()

    uploaded_file = st.file_uploader("Upload file link (.txt)", type=['txt'])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        st.success("✅ File berhasil diupload!")
        st.divider()
        
        # Mulai proses scraping
        if st.button("🚀 Mulai Scraping"):
            if "USERNAME" in st.session_state and "PASSWORD" in st.session_state:
                with st.spinner("Scraping komentar..."):
                    driver = create_driver()
                    login_success = login_instagram(driver, st.session_state["USERNAME"], st.session_state["PASSWORD"])
                    if login_success:
                        df = alat_scraper(temp_path, driver)
                        driver.quit()
                        st.success("✅ Scraping selesai!")
                        st.write(df)
                        st.download_button("⬇️ Download CSV", df.to_csv(index=False), file_name="komentar.csv")
                        st.session_state["data_scraping"] = df
                    else:
                        st.error("Gagal login ke Instagram.")

# Simulasi halaman 2: Analisis Sentimen
elif current_page == "Analisis Sentimen":
    st.header("🧠 Analisis Sentimen Komentar")
    def tampilkan_hasil(df):
        # Fungsi untuk menampilkan hasil analisis
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

# Simulasi halaman 3: Visualisasi
elif current_page == "Visualisasi":
    st.header("📊 Visualisasi Sentimen")
    
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
        st.warning("⚠️ Belum ada data untuk divisualisasi. Silakan scraping terlebih dahulu.")
