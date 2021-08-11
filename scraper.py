from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pathlib
from bs4 import BeautifulSoup, NavigableString
import json
from math import ceil
import pandas as pd
import sys

base_urls = [
    'https://onlyfinder.com/profiles?q=location:51.5116,-0.1312,500km', # London
    'https://onlyfinder.com/profiles?q=location:56.0399,-3.9220,500km', # Edinburgh
    'https://onlyfinder.com/profiles?q=location:51.9391,-8.4420,500km', # Cork
]

base_url = base_urls[2]

base_dir = str(pathlib.Path().resolve())
num_results = 1000

def downloadData():
    entries = []

    for i in range(ceil(num_results / 26)):
        options = Options()
        driver_path = ''
        if (sys.platform == 'win32'):
            print("detected Windows platform")
            driver_path = base_dir + '\chromedriver_win32\chromedriver.exe'
            options.binary_location = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        elif (sys.platform == 'darwin'):
            print("detected Mac platform")
            driver_path = base_dir + '/chromedriver_mac64/chromedriver'
            options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(executable_path=driver_path, options=options)
        
        url = base_url + '&c=' + str((i) * 26)
    
        driver.get(url)
    
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "result"))
            )
        except:
            driver.quit()

        results = driver.page_source
        driver.quit()
        
        soup = BeautifulSoup(results, 'html.parser')        

        for result in soup.find_all("div", class_="result"):
            entry = {}
            entry['id'] = len(entries) + 1
            entry['username'] = result.find("a")['data-username']
            entry['profile'] = result.find("a")['href']
            social_media = [x['href'] for x in result.find_all("a")[2:]]
            entry['social_media'] = social_media
            for site in ('instagram', 'twitter'):
                site_entry = [url for url in social_media if site in url]
                for j in (1, 2):
                    try:
                        entry[f'{site}_{j}'] = site_entry[j - 1]
                    except:
                        entry[f'{site}_{j}'] = ""
            entry['likes'] = []
            stats = result.find("div", class_="profile-info").find_all('span')
            if len(stats) == 4:
                entry['likes'] = int(stats[0].get_text().strip().replace(',', ''))
                entry['subscribers'] = ''
                entry['photos'] = int(stats[1].get_text().strip().replace(',', ''))
                entry['videos'] = int(stats[2].get_text().strip().replace(',', ''))
                entry['price'] = stats[3].get_text().replace('Price: ', '').strip()
            elif len(stats) == 5:
                entry['likes'] = int(stats[0].get_text().strip().replace(',', ''))
                entry['subscribers'] = int(stats[1].get_text().strip().replace(',', ''))
                entry['photos'] = int(stats[2].get_text().strip().replace(',', ''))
                entry['videos'] = int(stats[3].get_text().strip().replace(',', ''))
                entry['price'] = stats[4].get_text().replace('Price: ', '').strip()
            entries.append(entry)

        jsonFile = open("data.json", "w")
        jsonFile.write(json.dumps(entries))
        jsonFile.close()


def convert_json_to_csv():
    df = pd.read_json("data.json")
    df.to_csv('data.csv')

def main():   
    downloadData()
    convert_json_to_csv()
    

if __name__ == '__main__':
    main()
