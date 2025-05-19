def main():
    login_instagram(driver)

    links_file = file
    if not os.path.exists(links_file):
        logger.error(f"File {links_file} tidak ditemukan!")


    # Baca daftar URL
    with open(links_file, 'r') as file:
        links = [line.strip() for line in file if line.strip()]

    logger.info('Berhasil membaca file')


    all_results = []

    for i, url in enumerate(links):
        logger.info(f"Memproses {i+1}/{len(links)}: {url}")
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

    df = pd.DataFrame(all_results)
    logger.info(f"Berhenti Scraping. Total: {len(all_results)} komentar")

if __name__ == "__main__":
    main()