from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time
import requests
import os
import csv

# Initialize the driver (without additional options)
driver = webdriver.Chrome()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("sec_filings.log"),
        logging.StreamHandler()
    ]
)

STATE_FILE = "state_file.csv"
DIR = "sec_filings"
HEADERS = {
    "User-Agent": "SEC-Filings-Cyentia/1.0 (ravon@vt.edu)"
}

def main():
    driver = webdriver.Chrome()
    driver.get("https://www.sec.gov/edgar/search/#/q=%2522Item*1.05*Material*Cybersecurity*Incidents%2522&category=custom&forms=8-K")
    
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "preview-file"))
    )

    htm_files = []
    filings = loadState()
    
    # Extract links from the page
    links = driver.find_elements(By.CLASS_NAME, "preview-file")
    logging.info(f"Located {len(links)} filings")

    for link in links:
        link.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "open-file"))
        )

        document_link = driver.find_element(By.ID, "open-file").get_attribute("href")
        filename = os.path.basename(document_link)

        if filename not in filings:
            htm_files.append((document_link, filename))
        else:
            logging.info(f"Filing {filename} already in sec_filings")

        close_button = driver.find_element(By.ID, "close-modal")
        close_button.click()

    # download files
    for url, filename in htm_files:
        path = os.path.join(DIR, filename)
        if downloadFile(url, path):
            updateState(filename)

def loadState():
    if not os.path.exists(STATE_FILE):
        return set() # returns empty set
    
    with open(STATE_FILE, "r") as file:
        reader = csv.reader(file)
        return {row[0] for row in reader} #returns set
    
def updateState(filing):
    with open(STATE_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([filing, time.strftime("%Y-%m-%d %H:%M:%S")])

def downloadFile(url, filename):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response.text)
        logging.info(f"Downloaded {filename}")
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download {url}: {e}")
        return False

if __name__ == '__main__':
    main()