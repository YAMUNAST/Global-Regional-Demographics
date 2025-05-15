from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import csv
import re
import time

# Utility functions
def clean_number(text):
    return re.sub(r"[^\d]", "", text)

def clean_text(text):
    return re.sub(r"\[[^\]]*\]", "", text).strip()

def scroll_page(driver):
    # Scroll slowly line by line
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    for i in range(0, scroll_height, 100):  # scroll down in steps of 100 pixels
        driver.execute_script(f"window.scrollTo(0, {i});")
        time.sleep(0.05)  # Adjust speed if needed

# Configure Chrome
chrome_path = r"C:\mern\selenuimclg\chromedriver-win64\chromedriver.exe"  # Update if needed
service = Service(chrome_path)
options = webdriver.ChromeOptions()
# Remove headless mode to see browser
# options.add_argument("--headless")  

### Script 1: UN Population Data ###
driver1 = webdriver.Chrome(service=service, options=options)
driver1.get("https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)")
scroll_page(driver1)

try:
    wait = WebDriverWait(driver1, 10)
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.wikitable")))
    headers = [th.text.replace("\n", " ").strip() for th in table.find_elements(By.TAG_NAME, "th")]

    rows = table.find_elements(By.TAG_NAME, "tr")
    data = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        if cells:
            row_data = [cell.text.strip() for cell in cells]
            for i in [1, 2]:  # Clean population columns
                if i < len(row_data):
                    row_data[i] = "".join([char for char in row_data[i] if char.isdigit()])
            data.append(row_data)

    with open("population_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    print("Script 1: Saved to population_data.csv")
except Exception as e:
    print("Script 1 Error:", e)
driver1.quit()

### Script 2: India 2011 Census ###
driver2 = webdriver.Chrome(service=service, options=options)
driver2.get("https://en.wikipedia.org/wiki/2011_census_of_India")
scroll_page(driver2)

try:
    wait = WebDriverWait(driver2, 10)
    tables = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.wikitable")))

    target_table = None
    for table in tables:
        if "Population distribution in India by states" in table.text:
            target_table = table
            break

    if not target_table:
        raise Exception("Target table not found.")

    rows = target_table.find_elements(By.TAG_NAME, "tr")
    headers = [
        "State / Union Territory", "Capital", "Type", "Population",
        "Male", "Female", "Sex Ratio", "Literacy Rate",
        "Rural Population", "Urban Population",
        "Area (km²)", "Population Density", "Decade Growth (%)"
    ]
    data = []
    for row in rows[1:]:
        cells = row.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 14:
            row_data = [
                clean_text(cells[0].text), clean_text(cells[1].text), clean_text(cells[2].text),
                clean_number(cells[3].text), clean_number(cells[5].text), clean_number(cells[6].text),
                clean_text(cells[7].text), clean_text(cells[8].text),
                clean_number(cells[9].text), clean_number(cells[10].text),
                clean_number(cells[11].text), clean_number(cells[12].text),
                clean_text(cells[13].text)
            ]
            data.append(row_data)

    with open("india_population_2011_corrected.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    print("Script 2: Saved to india_population_2011_corrected.csv")
except Exception as e:
    print("Script 2 Error:", e)
driver2.quit()

### Script 3: Karnataka Districts ###
driver3 = webdriver.Chrome(service=service, options=options)
url3 = "https://www.census2011.co.in/census/state/districtlist/karnataka.html"
driver3.get(url3)
scroll_page(driver3)

time.sleep(2)
rows = driver3.find_elements(By.CSS_SELECTOR, "table tr")[1:]

district_data = []
for row in rows:
    cols = row.find_elements(By.TAG_NAME, "td")
    if len(cols) >= 8:
        district_data.append([
            cols[0].text.strip(), cols[1].text.strip(), cols[2].text.strip(),
            cols[3].text.strip(), cols[4].text.strip(), cols[5].text.strip(),
            cols[6].text.strip(), cols[7].text.strip()
        ])

with open("karnataka_districts_2011.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow([
        "District Code", "District Name", "Sub-Districts", "Population",
        "Increase (%)", "Sex Ratio", "Literacy (%)", "Density"
    ])
    writer.writerows(district_data)
print("Script 3: Saved to karnataka_districts_2011.csv")
driver3.quit()
