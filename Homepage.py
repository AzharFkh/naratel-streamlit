import streamlit as st
from scraper import create_driver, login_instagram, alat_scraper
import tempfile
from tools import sidebar_ui, page_style

st.set_page_config(page_title="Homepage", layout="wide")
st.title("🏠 Sentiment Analysis Tools")

sidebar_ui()
page_style()

# ➡️ Langkah penggunaan
st.markdown("""
## 📋 Langkah-langkah Penggunaan:
1. **Masukan Username** dan **Password** untuk login
2. **Upload file** berisi daftar link Instagram (format `.txt`).
3. **Masuk ke halaman Analisa Sentimen** setelah scraping selesai.
4. **Klik tombol "Mulai Analisa Sentimen"** untuk memproses data.
5. **Lihat hasil Analisa Sentimen** di halaman Hasil Analisa.   
""")

st.divider()

# Form untuk mengisi username dan password Instagram
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
        else:
            st.error("⚠️ Silakan login terlebih dahulu.")

elif "data_scraping" in st.session_state:
    st.subheader("📄 Data Scraping Sebelumnya")
    st.dataframe(st.session_state["data_scraping"])

else:
    st.warning("⚠️ Menunggu file di upload")
