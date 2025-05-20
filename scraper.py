from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import logging
import os
from dotenv import load_dotenv

# untuk logging tools
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# untuk membuka file env
env_path = os.path.join(os.getcwd(), r'C:') #masukan file path dengan file .env
load_dotenv(dotenv_path=env_path)

# ambil password
USERNAME = os.getenv('INSTAGRAM_USERNAME')
PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
Max_Comment = 200

def create_driver():
    # Siapkan driver Chrome
    chrome_options = Options()
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")    
    chrome_options.add_argument("--disable-dev-shm-usage") 
    chrome_options.add_argument("--disable-gpu") 

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def login_instagram(driver, username=USERNAME, password=PASSWORD):
    """Fungsi untuk login ke Instagram."""
    try:
        
        driver.get("https://www.instagram.com/accounts/login/?next=https%3A%2F%2Fwww.instagram.com%2Fexample%2F&is_from_rle")
        time.sleep(3)
        
        # Login dengan username dan password
        username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
        username_field.send_keys(username)
        
        time.sleep(3)

        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'password')))
        password_field.send_keys(password)
        
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
        login_button.click()
        time.sleep(5)
        
        # Handle popup "Not Now" jika muncul
        try:
            not_now = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Not Now")]')))
            not_now.click()
        except:
            pass
            
        return True
    except Exception as e:
        logger.error(f"Login gagal: {e}")
        return False

def extract_comments_from_selector(driver, selector):
    """Fungsi helper untuk mengekstrak komentar dari selector tertentu."""
    comments = []
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        
        for element in elements:
            try:
                # Coba berbagai metode untuk mengekstrak teks
                text = ""
                try:
                    text = element.text
                except:
                    try:
                        text = element.get_attribute('innerText')
                    except:
                        pass
                
                # Tambahkan komentar yang valid
                if text and len(text) > 1:
                    comments.append(text)
            except Exception as e:
                logger.debug(f"Gagal ekstrak teks dari elemen: {e}")
        
        return comments
    except Exception as e:
        logger.debug(f"Selector '{selector}' gagal: {e}")
        return []

def scrape_comments(driver, url, max_comments=500):
    """Fungsi untuk mengambil komentar dari postingan Instagram."""
    comments = []
    collected_comments = 0
    target_comments = max_comments
    
    try:
        # Buka halaman postingan
        driver.get(url)
        time.sleep(3)  # Sedikit lebih lama untuk memastikan halaman dimuat sepenuhnya
        
        # Comment selector utama yang akan digunakan
        main_selector = 'div.x9f619.xjbqb8w.x78zum5.x168nmei.x13lgxp2.x5pf9jr.xo71vjh.x1uhb9sk.x1plvlek.xryxfnj.x1c4vz4f.x2lah0s.xdt5ytf.xqjyukv.x1cy8zhl.x1oa3qoh.x1nhvcw1 > span'

        # Coba ambil komentar langsung tanpa scroll terlebih dahulu
        initial_comments = extract_comments_from_selector(driver, main_selector)
        for comment in initial_comments:
            if comment not in comments and len(comments) < target_comments:
                comments.append(comment)
    
        collected_comments = len(comments)
        logger.info(f"Terkumpul awal: {collected_comments} komentar")
        
        # Jika sudah mencapai target atau tidak ada komentar untuk di-scroll, selesai
        if collected_comments >= target_comments:
            logger.info(f"Target komentar tercapai tanpa scroll")
            return comments
        
        # Scroll dan kumpulkan komentar hingga mencapai target
        max_attempts = 30  # Batasi jumlah percobaan untuk menghindari loop tak berakhir
        attempts = 0
        no_progress_count = 0
        
        while collected_comments < target_comments and attempts < max_attempts and no_progress_count < 2:
            attempts += 1
            prev_comment_count = len(comments)
            
            try:
                # Coba temukan elemen untuk scroll
                try:
                    # Coba temukan elemen xemfg65 jika ada
                    element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "xemfg65"))
                    )
                    # Scroll ke elemen tersebut
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                except:
                    logger.info("Elemen tidak ditemukan")
                    # Jika tidak menemukan elemen xemfg65, scroll ke bagian bawah general
                    #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                time.sleep(2)  # Tunggu untuk konten dimuat
                
                # Coba selector utama terlebih dahulu
                new_comments = extract_comments_from_selector(driver, main_selector)

                # Tambahkan komentar unik ke daftar
                for comment in new_comments:
                    if comment not in comments and len(comments) < target_comments:
                        comments.append(comment)
                
                # Perbarui jumlah komentar yang dikumpulkan
                collected_comments = len(comments)
                logger.info(f"Terkumpul {collected_comments} komentar (Percobaan {attempts})")
                
                # Cek jika tidak ada komentar baru yang ditambahkan
                if len(comments) == prev_comment_count:
                    no_progress_count += 1
                    logger.info(f"Tidak ada komentar baru")
                else:
                    no_progress_count = 0  # Reset jika ada progress

            except Exception as e:
                logger.warning(f"Error saat scroll: {e}")
                time.sleep(2)
                no_progress_count += 1
        
        # Alasan keluar dari loop
        if collected_comments >= target_comments:
            logger.info(f"Berhasil mengumpulkan {prev_comment_count} komentar")
    
        else:
            #logger.info(f"Berhenti Scraping. Total: {prev_comment_count} komentar")
            pass
        return comments
    
    except Exception as e:
        logger.error(f"Gagal mengambil komentar: {e}")
        return comments
    
def alat_scraper(link_postingan, driver):
    
    all_results = []

    with open(link_postingan, 'r') as file:
        links = [line.strip() for line in file if line.strip()]
        total = len(link_postingan)
    logger.info('Berhasil membaca file')

    for i, url in enumerate(links):
        logger.info(f"Memproses {i+1}/{total}: {url}")
        post_id = url.split('/')[-2] if '/' in url else f"post_{i+1}"
        
        comments = scrape_comments(driver, url)
        
        for comment in comments:
            all_results.append({
                'Post URL': url,
                'Post ID': post_id,
                'Komentar': comment
            })
        
        time.sleep(2)

    df = pd.DataFrame(all_results)
    logger.info(f"Scraping selesai. Total komentar: {len(all_results)}")
    return df

def main():
    links_file = 'link.txt'
    if not os.path.exists(links_file):
        logger.error(f"File {links_file} tidak ditemukan!")
    
    driver = create_driver()
    login_instagram(driver)

    if not os.path.exists(links_file):
        logger.error(f"File {links_file} tidak ditemukan!")


    with open(links_file, 'r') as file:
        links = [line.strip() for line in file if line.strip()]

    logger.info('Berhasil membaca file')

    all_results = []
            
    # Proses setiap link
    for i, url in enumerate(links):
        logger.info(f"Memproses {i+1}: {url}")
        post_id = url.split('/')[-2] if '/' in url else f"post_{i+1}"
        
        # Ambil komentar
        comments = scrape_comments(driver, url)
        
        # Simpan hasil
        for comment in comments:
            all_results.append({
                'Post URL': url,
                'Post ID': post_id,
                'Komentar': comment
            })
        
        # Jeda sebelum link berikutnya
        time.sleep(2)

    logger.info(f"Berhenti Scraping. Total: {len(all_results)} komentar")

if __name__ == "__main__":
    main()