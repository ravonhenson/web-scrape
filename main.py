from selenium import webdriver
from selenium.webdriver.common.by import By

import time
import requests
import os

# Initialize the driver (without additional options)
driver = webdriver.Chrome()

try:
    # Navigate to the page
    driver.get("https://www.sec.gov/edgar/search/#/q=%2522Item*1.05*Material*Cybersecurity*Incidents%2522&category=custom&forms=8-K")
    
    # Wait for the page to load completely
    time.sleep(3)

    htm_files = []
    
    # Extract links from the page
    links = driver.find_elements(By.CLASS_NAME, "preview-file")
    print(f"Searching through {len(links)} elements. Estimated time: {len(links) * 3} seconds ")

    for link in links:  #[:1] temporary for testing
        link.click()
        time.sleep(2)

        document_link = driver.find_element(By.ID, "open-file").get_attribute("href")
        htm_files.append(document_link)

        close_button = driver.find_element(By.ID, "close-modal")
        close_button.click()
        time.sleep(1)

finally:
    # Close the driver
    dir = "sec_filings"
    os.makedirs(dir, exist_ok=True)

    headers = {
    "User-Agent": "SEC-Filings-Cyentia/1.0 (ravon@vt.edu)"
    }
    
    for url in htm_files:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            filename = os.path.join(dir, os.path.basename(url))

            with open(filename, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"Successfully downloaded {filename}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to download: {e}")    
    driver.quit()