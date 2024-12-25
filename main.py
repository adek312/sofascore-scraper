import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Ustawienia WebDrivera
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Otwórz stronę
# url = "https://www.sofascore.com/pl/zawodnik/cristiano-ronaldo/750#tab:matches"
url = "https://www.sofascore.com/pl/zawodnik/alessandro-del-piero/2088#tab:matches"
# url = "https://www.sofascore.com/pl/zawodnik/erling-haaland/839956"
driver.get(url)

# Zamknięcie Ciasteczek
try:
    modal_close_button = driver.find_element(By.CSS_SELECTOR, '.fc-button-label')
    modal_close_button.click()
except Exception as e:
    print("Brak modalnego okna do zamknięcia.")

# Wejście w zakładkę meczy
try:
    matches_tab = driver.find_element(By.CSS_SELECTOR, '[href="#tab:matches"]')  # Znajdź zakładkę "Mecze"
    matches_tab.click()
    print("Kliknięto zakładkę 'Mecze'.")
except Exception as e:
    print(f"Błąd podczas kliknięcia zakładki 'Mecze': {e}")

# Poczekaj, aż strona się załaduje
time.sleep(5)

# Przewiń stronę, aby załadować wszystkie mecze (jeśli ładowane dynamicznie)
scroll_pause_time = 2
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(scroll_pause_time)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Znajdź listę meczów
matches = driver.find_elements(By.CSS_SELECTOR, "[data-testid='event_cell']")  
print(f"Znaleziono {len(matches)} meczów")

data = []

# Zbieramy dane o meczach i ocenach
for i, match in enumerate(matches):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='event_cell']"))
        )
        
        # Pobierz datę meczu
        date = match.find_element(By.CSS_SELECTOR, "[data-testid='event_time']").text
        # Pobierz drużyny
        teams = match.find_element(By.CSS_SELECTOR, ".jtsXPN").text
        # Pobierz wynik
        result = match.find_element(By.CSS_SELECTOR, ".yaNbA").text
        
        # Znajdź odpowiednią ocenę
        span_elements = driver.find_elements(By.XPATH, "//span[@aria-valuenow]")
        try:
            aria_value = span_elements[i].get_attribute('aria-valuenow')
        except IndexError:
            aria_value = "Brak oceny"

        
        # Dodaj dane meczu i ocenę do listy
        data.append({
            "Data": date,
            "Drużyny": teams,
            "Wynik": result,
            "Ocena": aria_value
        })

    except Exception as e:
        print(f"Błąd podczas parsowania meczu {i + 1}: {e}")

# Zapisz dane do pliku CSV
try:
    with open('mecze_i_oceny.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Data", "Drużyny", "Wynik", "Ocena"])
        writer.writeheader()
        writer.writerows(data)
    print("Dane zapisane do pliku 'mecze_i_oceny.csv'.")
except Exception as e:
    print(f"Błąd podczas zapisywania do pliku CSV: {e}")

finally:
    # Zamknij przeglądarkę
    driver.quit()
