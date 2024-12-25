from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import openpyxl

# Webdriver Init
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Sofascore Site
url = "https://www.sofascore.com/pl/zawodnik/cristiano-ronaldo/750"
driver.get(url)
player = url.split('/')[-2]
# Cookies
try:
    modal_close_button = driver.find_element(By.CSS_SELECTOR, '.fc-button-label')
    modal_close_button.click()
except Exception as e:
    print("No cookies to click")

# Enter matches tab
try:
    matches_tab = driver.find_element(By.CSS_SELECTOR, '[href="#tab:matches"]') 
    matches_tab.click()
    print("Enter Matches tab")
except Exception as e:
    print(f"Error while entering matches tab: {e}")
time.sleep(5)


# Scroll to bottom to load every match
scroll_pause_time = 2
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1500);")
    time.sleep(scroll_pause_time)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Download all matches
matches = driver.find_elements(By.CSS_SELECTOR, "[data-testid='event_cell']")  
print(f"Found {len(matches)} matches")

data = []

# Gather specific data
for i, match in enumerate(matches):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='event_cell']"))
        )
        
        date = match.find_element(By.CSS_SELECTOR, "[data-testid='event_time']").text
        
        teams_raw = match.find_element(By.CSS_SELECTOR, ".jtsXPN").text
        teams = teams_raw.replace("\n", " ").strip()
        
        result_raw = match.find_element(By.CSS_SELECTOR, ".yaNbA").text
        result = result_raw.replace("\n", ":").strip()
        
        rating_raw = driver.find_elements(By.XPATH, "//span[@aria-valuenow]")
        try:
            rating = rating_raw[i].get_attribute('aria-valuenow')
        except IndexError:
            rating = "N.D"

        
        # Add all gathered data to dictionary
        data.append({
            "Date": date,
            "Teams": teams,
            "Result": result,
            "Rating": rating
        })

    except Exception as e:
        print(f"Match parse error {i + 1}: {e}")

try:
    # Create excel
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = f"Sofascore_{player}"
    
    sheet["A1"] = "Date"
    sheet["B1"] = "Teams"
    sheet["C1"] = "Result"
    sheet["D1"] = "Rating"
    
    for i, match_data in enumerate(data, start=2):  
        sheet[f"A{i}"] = match_data["Date"]
        sheet[f"B{i}"] = match_data["Teams"]
        sheet[f"C{i}"] = match_data["Result"]
        sheet[f"D{i}"] = match_data["Rating"]

    wb.save(f"Sofascore_{player}.xlsx")
    print(f"Data saved to file: 'Sofascore_{player}.xlsx'.")

except Exception as e:
    print(f"Saving excel Error: {e}")

finally:
    driver.quit()