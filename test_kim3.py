from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def run():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    url = "https://www.kimchang.com/ko/insights/index.kc?sch_keyword=부동산"
    driver.get(url)
    
    try:
        # Wait for list items to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li .tit"))
        )
        time.sleep(2) # Extra wait for rendering
        
        items = driver.find_elements(By.CSS_SELECTOR, "li")
        results = []
        for item in items:
            text = item.text.strip()
            if "부동산" in text or "임대차" in text:
                results.append(text.replace('\n', ' '))
                
        # Also try to extract specific titles
        titles = driver.find_elements(By.CSS_SELECTOR, ".tit")
        for t in titles:
            if t.text.strip():
                results.append("Title: " + t.text.strip())
                
        open('kim_selenium.txt', 'w', encoding='utf-8').write("\n".join(results[:50]))
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run()
