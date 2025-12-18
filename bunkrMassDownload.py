from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver as webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def create_headless_browser(download_dir: str = None) -> webdriver:
    print("Creating headless browser...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set download directory
    if download_dir:
        prefs = {
            "download.default_directory": str(download_dir),
            "download.prompt_for_download": False,
            "profile.default_content_settings.popups": 0,
            "safebrowsing.enabled": True,
        }
        chrome_options.add_experimental_option("prefs", prefs)

    browser = webdriver(options=chrome_options)

            
    print(f"Headless browser created: {browser}")
    return browser

def get_items_from_album(webdriver_instance: webdriver, album_url: str) -> list:
    print(f"Fetching items from album: {album_url}")
    webdriver_instance.get(album_url)
    items = webdriver_instance.find_elements(By.CSS_SELECTOR,"#galleryGrid a[href]")
    item_urls = [item.get_attribute("href") for item in items]
    print(f"Found {len(item_urls)} items in album.")
    return item_urls

def get_data_from_item(webdriver_instance: webdriver, item_url: str) -> str:
    print(f"Fetching data from item: {item_url}")
    webdriver_instance.get(item_url)
    download_link = webdriver_instance.find_element(By.LINK_TEXT, "Download").get_attribute("href")
    print(f"Download link found: {download_link}")
    return download_link

def download_file(webdriver_instance: webdriver, download_url: str, download_dir: str = None, timeout: int = 600) -> None:
    print(f"Starting download for: {download_url} to {download_dir or 'default download directory'}")
    import os
    import time

    if not download_dir:
        download_dir = os.getcwd()
    download_dir = os.path.abspath(download_dir)
    os.makedirs(download_dir, exist_ok=True)

    before = set(os.listdir(download_dir))

    webdriver_instance.get(download_url)
    webdriver_instance.find_element(By.ID, "download-btn").click()

    temp_suffixes = ('.crdownload', '.tmp', '.part')
    start = time.time()

    print(f"Waiting for download to start in {download_dir} (timeout {timeout}s)")

    last_sizes = {}
    while True:
        if time.time() - start > timeout:
            raise TimeoutError(f"Timed out waiting for download of {download_url} in {download_dir}")

        now = set(os.listdir(download_dir))
        new_files = now - before
        if not new_files:
            time.sleep(0.5)
            continue

        # Check for temp files
        completed_files = []
        seen_temp = False
        for fname in new_files:
            if fname.lower().endswith(temp_suffixes):
                seen_temp = True
                # Get size
                full = os.path.join(download_dir, fname)
                try:
                    size = os.path.getsize(full)
                except OSError:
                    size = -1
                last_sizes[fname] = size
            else:
                # Likely completed file, verify size stability
                full = os.path.join(download_dir, fname)
                try:
                    size1 = os.path.getsize(full)
                except OSError:
                    size1 = -1
                time.sleep(0.5)
                try:
                    size2 = os.path.getsize(full)
                except OSError:
                    size2 = -1
                if size1 == size2 and size1 > 0:
                    completed_files.append(full)
                else:
                    seen_temp = True

        # If there are temp files, wait until they disappear and sizes stabilize
        if seen_temp:
            # Wait a short time and continue polling
            time.sleep(1)
            continue

        if completed_files:
            for f in completed_files:
                print(f"Download completed: {f}")
            return

        time.sleep(0.5)




def main(**kwargs) -> None:
    print("Bunkr Mass Downloader")
    import os

    _ALBUM_URL = kwargs.get("album_url", None)
    _DESTINATION_PATH = kwargs.get("destination_path", None)
    
    if not _ALBUM_URL:
        _ALBUM_URL = input("Enter the Bunkr album URL: ").strip()
    
    if not _DESTINATION_PATH:
        _DESTINATION_PATH = input("Enter download destination (leave blank for current directory): ").strip()
        if _DESTINATION_PATH == "":
            _DESTINATION_PATH = os.getcwd()
        else:
            _DESTINATION_PATH = os.path.expanduser(_DESTINATION_PATH)

    browser = create_headless_browser(download_dir=_DESTINATION_PATH)
    
    try:
        print("Starting download process...")
        item_urls = get_items_from_album(browser, _ALBUM_URL)
        for item_url in item_urls:
            download_link = get_data_from_item(browser, item_url)
            download_file(browser, download_link, download_dir=_DESTINATION_PATH)
    finally:
        print("Closing browser...")
        browser.quit()
    print("All downloads completed.")

if __name__ == "__main__":
    main()