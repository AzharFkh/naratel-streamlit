import streamlit as st
from scraper import create_driver, login_instagram, alat_scraper
from analisa_roberta import analyze_sentiment
import plotly.express as px
import pandas as pd
import tempfile
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Atur halaman
st.set_page_config(
    page_title="Sentimen Analisis IG",
    layout="wide",  # Tetap wide untuk visualisasi enak
    initial_sidebar_state="expanded"
)

# Sidebar navigasi
st.sidebar.title("Navigasi")
current_page = st.sidebar.radio("Pilih halaman:", ["Upload & Scrape", "Analisis Sentimen", "Visualisasi"])

# Judul utama
st.title("📱 Sentimen Analisis Sosial Media Kapten Naratel")

# ==================== HALAMAN 1: Upload & Scrape ====================
if current_page == "Upload & Scrape":
    with st.form(key='login_form'):
        st.subheader("🔑 Login Instagram")
        USERNAME = st.text_input("Username Instagram")
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

    uploaded_file = st.file_uploader("📂 Upload file link (.txt)", type=['txt'])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name

        st.success("✅ File berhasil diupload!")
        st.divider()

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
                        st.error("❌ Gagal login ke Instagram.")

# ==================== HALAMAN 2: Analisis Sentimen ====================
elif current_page == "Analisis Sentimen":
    st.header("🧠 Analisis Sentimen Komentar")

    def tampilkan_hasil(df):
        st.subheader("➡️ Hasil Analisis Sentimen")
        st.dataframe(df[st.session_state["Kolom ditampilkan"]])

    def proses_analisis(df):
        with st.spinner("🔎 Sedang menganalisis..."):
            result_df = analyze_sentiment(df, text_column="Komentar")
            st.session_state["hasil_analisa"] = result_df.copy()
            st.session_state["Kolom ditampilkan"] = ["Post URL", "Komentar", "Label Sentimen"]
            st.session_state["data_label"] = result_df["Label Sentimen"].value_counts()
            st.success("✅ Analisis selesai, periksa di halaman Visualisasi!")

    if "data_scraping" in st.session_state:
        data_analisa = st.session_state["data_scraping"].copy()
        st.dataframe(data_analisa)

        if st.button("🚀 Mulai Analisis Data"):
            proses_analisis(data_analisa)

    else:
        st.warning("⚠️ Belum ada data untuk dianalisis. Silakan scraping terlebih dahulu.")

# ==================== HALAMAN 3: Visualisasi ====================
elif current_page == "Visualisasi":
    st.header("📊 Visualisasi Sentimen")

    if "hasil_analisa" in st.session_state and "Kolom ditampilkan" in st.session_state:
        # Gunakan .copy() untuk menghindari modifikasi data asli di session_state secara tidak sengaja
        data_diolah_lengkap = st.session_state["hasil_analisa"].copy()
        kolom_ditampil_awal = st.session_state["Kolom ditampilkan"]

        # Pastikan kolom yang diperlukan ada di data_diolah_lengkap
        required_cols = ["Post URL", "Komentar", "Label Sentimen"]
        if not all(col in data_diolah_lengkap.columns for col in required_cols):
            st.error(f"Data hasil analisis tidak lengkap. Kolom yang dibutuhkan: {', '.join(required_cols)} tidak ditemukan.")
            st.stop()


        df_semua_data = pd.DataFrame(data_diolah_lengkap) # DataFrame untuk semua data

        # --- 1. GROUPED BAR CHART (PERBANDINGAN SEMUA POST) ---
        st.divider()
        st.subheader("📊 Perbandingan Sentimen Antar Semua Link Unggahan")
        if not df_semua_data.empty:
            sentiment_counts_all_posts = df_semua_data.groupby(['Post URL', 'Label Sentimen']).size().reset_index(name='Jumlah')
            if not sentiment_counts_all_posts.empty:
                fig_grouped_bar = px.bar(
                    sentiment_counts_all_posts,
                    x='Post URL',
                    y='Jumlah',
                    color='Label Sentimen',
                    barmode='group',
                    title="Distribusi Sentimen per Link Unggahan",
                    labels={'Post URL': 'Link Unggahan', 'Label Sentimen': 'Sentimen', 'Jumlah': 'Jumlah Komentar'},
                    color_discrete_map={
                        'Positif': 'mediumseagreen',
                        'Negatif': 'indianred',
                        'Netral': 'lightskyblue'
                    },
                    height=max(500, len(df_semua_data['Post URL'].unique()) * 50) # Tinggi dinamis
                )
                fig_grouped_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_grouped_bar, use_container_width=True)
            else:
                st.info("Tidak ada data yang cukup untuk membuat grouped bar chart.")
        else:
            st.info("Tidak ada data hasil analisis untuk ditampilkan.")


        # --- 2. FITUR YANG SUDAH ADA (PIE CHART, STATISTIK, FILTER KOMENTAR PER POST/SEMUA) ---
        st.divider()
        st.subheader("📌 Analisis Detail per Post atau Keseluruhan")

        # Menggunakan df_semua_data untuk mendapatkan daftar post unik
        daftar_post = ["Semua Post"] + df_semua_data["Post URL"].unique().tolist()
        selected_post = st.selectbox("Pilih Post URL untuk Analisis Detail:", options=daftar_post, key="detail_post_select")

        # Filter data berdasarkan pilihan dropdown
        if selected_post == "Semua Post":
            df_filtered = df_semua_data.copy() # Gunakan copy
        else:
            df_filtered = df_semua_data[df_semua_data["Post URL"] == selected_post].copy() # Gunakan copy

        if not df_filtered.empty:
            st.subheader(f"➡️ Statistik Sentimen untuk: {selected_post}")
            if "Label Sentimen" in df_filtered.columns:
                jumlah_sentimen_filtered = df_filtered["Label Sentimen"].value_counts().reset_index()
                jumlah_sentimen_filtered.columns = ["Sentimen", "Jumlah"]

                st.write(f"Jumlah Komentar: {df_filtered.shape[0]}")
                c1, c2, c3 = st.columns(3)
                sentimen_map = dict(zip(jumlah_sentimen_filtered['Sentimen'], jumlah_sentimen_filtered['Jumlah']))
                c1.metric("🙂 Positif", sentimen_map.get("Positif", 0))
                c2.metric("😐 Netral", sentimen_map.get("Netral", 0))
                c3.metric("🙁 Negatif", sentimen_map.get("Negatif", 0))

                st.markdown("---") # Pemisah sebelum pie chart
                st.subheader(f"🥧 Distribusi Sentimen untuk: {selected_post}")
                if not jumlah_sentimen_filtered.empty:
                    fig_pie = px.pie(
                        jumlah_sentimen_filtered,
                        names="Sentimen",
                        values="Jumlah",
                        color_discrete_sequence=px.colors.qualitative.Set2 # Ganti palet warna jika ingin
                    )
                    fig_pie.update_layout(height=500) # Ukuran bisa disesuaikan
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Tidak ada data sentimen untuk ditampilkan pada pie chart untuk pilihan ini.")

                # --- 3. WORD CLOUD (MENGGUNAKAN DATA YANG SAMA DENGAN PIE CHART) ---
                st.markdown("---") # Pemisah sebelum word cloud
                st.subheader(f"☁️ Word Cloud untuk: {selected_post}")
                if "Komentar" in df_filtered.columns and not df_filtered.empty:
                    text_corpus = " ".join(comment for comment in df_filtered["Komentar"].astype(str) if pd.notnull(comment))
                    if text_corpus.strip():
                        #  bisa menambahkan stopwords di sini jika perlu
                        # stopwords_custom = set(["yang", "dan", "di", "ini", "itu", "saya", "kak", "min"])
                        try:
                            wordcloud = WordCloud(
                                width=800,
                                height=400,
                                background_color='white',
                                stopwords=None, # Ganti dengan stopwords_custom jika ada
                                collocations=False, # Menghindari bigram yang tidak diinginkan
                                min_font_size=10
                            ).generate(text_corpus)

                            fig_wc, ax = plt.subplots(figsize=(10, 5))
                            ax.imshow(wordcloud, interpolation='bilinear')
                            ax.axis("off")
                            st.pyplot(fig_wc)
                        except Exception as e:
                            st.error(f"Gagal membuat wordcloud: {e}")
                    else:
                        st.info("Tidak ada teks komentar yang cukup untuk membuat wordcloud untuk pilihan ini.")
                else:
                    st.info("Tidak ada kolom 'Komentar' atau data komentar untuk membuat wordcloud untuk pilihan ini.")


                # --- 4. FITUR YANG SUDAH ADA (TAMPILKAN KOMENTAR BERDASARKAN LABEL) ---
                st.markdown("---") # Pemisah sebelum filter komentar
                st.subheader(f"🔍 Tampilkan Komentar Berdasarkan Label untuk: {selected_post}")
                if not jumlah_sentimen_filtered.empty:
                    opsi_label = jumlah_sentimen_filtered["Sentimen"].tolist()
                    if opsi_label: # Pastikan ada opsi label
                        selected_sentimen_label = st.selectbox("Pilih Label Sentimen:", options=opsi_label, key="label_filter_select")
                        komentar_terfilter = df_filtered[df_filtered["Label Sentimen"] == selected_sentimen_label]

                        st.write(f"Menampilkan {len(komentar_terfilter)} komentar dengan label **{selected_sentimen_label}** dari '{selected_post}':")
                        # Tampilkan kolom yang relevan, sesuaikan dengan kebutuhan
                        st.dataframe(komentar_terfilter[["Post URL", "Komentar", "Label Sentimen"]])
                    else:
                        st.info("Tidak ada label sentimen untuk dipilih dalam filter ini.")
                else:
                    st.info("Tidak ada data sentimen untuk menampilkan komentar berdasarkan label untuk pilihan ini.")
            else:
                st.info("Kolom 'Label Sentimen' tidak ditemukan dalam data yang difilter.")
        else:
            st.info(f"Tidak ada data komentar untuk '{selected_post}'.")

    else:
        st.warning("⚠️ Belum ada data untuk divisualisasi. Silakan lakukan analisis sentimen terlebih dahulu di halaman 'Analisis Sentimen'.")
