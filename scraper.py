from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pathlib
from bs4 import BeautifulSoup, NavigableString
import json

url = 'https://onlyfinder.com/profiles?q=location:51.5116,-0.1312,500km'
base_dir = str(pathlib.Path().resolve())

def main():
    driver_path = base_dir + '\chromedriver_win32\chromedriver.exe'
    options = Options()
    options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(executable_path=driver_path, options=options)
    driver.get(url)
    time.sleep(3)

    # Handle infinite scrolling
    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    results = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(results, 'html.parser')
    
    entries = []

    for result in soup.find_all("div", class_="result"):
        entry = {}
        entry['id'] = len(entries) + 1
        entry['username'] = result.find("a")['data-username']
        entry['profile'] = result.find("a")['href']
        entry['social_media'] = [x['href'] for x in result.find_all("a")[2:]]
        entry['likes'] = []
        stats = result.find("div", class_="profile-info").find_all('span')
        entry['likes'] = int(stats[0].get_text().strip().replace(',', ''))
        entry['photos'] = int(stats[1].get_text().strip().replace(',', ''))
        entry['videos'] = int(stats[2].get_text().strip().replace(',', ''))
        entry['price'] = stats[3].get_text().replace('Price: ', '').strip()
        entries.append(entry)

    jsonFile = open("data.json", "w")
    jsonFile.write(json.dumps(entries))
    jsonFile.close()

if __name__ == '__main__':
    main()
