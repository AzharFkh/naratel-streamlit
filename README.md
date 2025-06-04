# 📊 Naratel Streamlit – Analisis Sentimen Komentar Instagram

Aplikasi Streamlit untuk melakukan scraping komentar dari postingan Instagram dan menganalisis sentimennya menggunakan model RoBERTa. Cocok untuk brand monitoring, riset pasar, dan analisis opini publik di media sosial.

---

## 🚀 Fitur Utama

* 🗂 Upload file `.txt` berisi daftar link postingan Instagram
* 🔐 Login otomatis ke Instagram menggunakan Selenium
* 🤖 Scraping komentar dari setiap postingan
* 🧐 Analisis sentimen dengan model RoBERTa
* 📅 Unduh hasil analisis dalam format CSV

---

## 🛠️ Instalasi

1. **Clone repositori ini:**

   ```bash
   git clone https://github.com/AzharFkh/naratel-streamlit.git
   cd naratel-streamlit
   ```

2. **Buat dan aktifkan virtual environment (opsional namun disarankan):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/macOS
   venv\Scripts\activate     # Untuk Windows
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Menjalankan Aplikasi

```bash
streamlit run main.py
```

---

## 📝 Format File Input

Buat file `.txt` yang berisi satu link Instagram per baris, contoh:

```
https://www.instagram.com/p/...
https://www.instagram.com/p/...
https://www.instagram.com/p/...
```

---

## 🔐 Login & Scraping

* Masukkan username dan password Instagram Anda melalui form login yang tersedia.
* Setelah login berhasil, proses scraping komentar akan berjalan otomatis untuk setiap link yang diunggah.

---

## 🤖 Analisis Sentimen

* Model akan memproses semua komentar dan memberikan label sentimen:

  * Positif 😊
  * Netral 😐
  * Negatif 😠
* Hasil analisis akan ditampilkan dalam tabel dan dapat diunduh dalam format CSV.

---

## 📁 Struktur Folder

```
.
├── main.py              # Halaman utama untuk upload & scraping
├── analisa_roberta.py   # Modul analisis sentimen dengan RoBERTa
├── scraper.py           # Fungsi scraping dengan Selenium
├── tools.py             # Fungsi bantu tambahan
├── requirements.txt     # Daftar dependencies
├── link.txt             # Contoh file input link Instagram
└── README.md            # Dokumentasi proyek ini
```

---

## ⚠️ Catatan Penting

* Pastikan akun Instagram Anda tidak menggunakan autentikasi dua faktor (2FA) untuk menghindari kegagalan login.
* Hindari memasukkan baris kosong dalam file `.txt` yang diunggah.
* Jangan terlalu banyak link dalam sekali scraping untuk menghindari pemblokiran oleh Instagram.

---

## 📬 Kontribusi

Proyek ini masih dalam tahap pengembangan. Silakan buat pull request atau buka issue untuk saran dan perbaikan.

---

## 🥡 Catatan Pengembang

Dibuat dengan semangat untuk mempermudah analisis sentimen komentar di Instagram menggunakan Python dan Streamlit.

---

Jika Anda memerlukan bantuan lebih lanjut atau memiliki pertanyaan, jangan ragu untuk menghubungi saya.
