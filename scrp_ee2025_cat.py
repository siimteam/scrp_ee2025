import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin

# Настройки
BASE_URL = "https://catalogue.ite-expo.ru/ru-RU/productcatalog.aspx?project_id=536"
OUTPUT_FILE_NAME = "scrp_ee2025_cat"
PAGES_TO_SCRAPE = 137  # Сколько страниц каталога обработать 
DELAY = 3  # Максимальное время ожидания элементов (секунды)

# Настройка Selenium
options = Options()
options.add_argument("--headless")  # Режим без графического интерфейса
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

def init_driver():
    """Инициализация веб-драйвера"""
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    return driver

def scrape_product_links(driver, url):
    """Извлекает ссылки на продукты с текущей страницы"""
    try:
        WebDriverWait(driver, DELAY).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".products_list"))) #rus
        
        product_links = []
        products = driver.find_elements(By.CSS_SELECTOR, ".products_list a[href]")
        
        for product in products:
            href = product.get_attribute("href")
            htext = product.get_attribute("text").replace("\n",";")
            if href and "product" in href.lower():
                full_url = urljoin(BASE_URL, href)  + htext
                product_links.append(full_url)
        
        return product_links
    
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Ошибка при загрузке страницы {url}: {str(e)}")
        return []

def find_next_page(driver, page_num):
    """Находит и кликает на кнопку следующей страницы"""
    try:
    
        next_btn = WebDriverWait(driver, DELAY).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="p_lt_zoneContainer_pageplaceholder_p_lt_ctl00_UniPagerProducts_pagerElem"]/a[contains(@href, "'+str(page_num)+'" )]'))) #
        
        if next_btn:
            next_url = next_btn.get_attribute("href")
            print(f"навигатор href: {next_url}")
            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(random.uniform(2, 4))  # Ожидание загрузки новой страницы
            return next_url
    
    except (TimeoutException, NoSuchElementException):
        print("Не удалось найти кнопку следующей страницы")
        return None

def main():
    driver = init_driver()
    all_links = []
    current_url = BASE_URL
    page_num = 1
    driver.get(current_url)
    try:
        while current_url:
            print(f"Обработка страницы {page_num}: {current_url}")
        
            # Получаем ссылки с текущей страницы
            page_links = scrape_product_links(driver, current_url)
            all_links.extend(page_links)
            print(f"Найдено ссылок: {len(page_links)} (всего: {len(all_links)})")
            
            # Проверяем лимит страниц
            if PAGES_TO_SCRAPE and page_num >= PAGES_TO_SCRAPE:
                break
            
            # Переходим на следующую страницу
            page_num += 1
            current_url = find_next_page(driver, page_num)
            time.sleep(random.uniform(2, 4))  # Ожидание загрузки новой страницы

            # Случайная задержка между запросами
            time.sleep(random.uniform(1, 3))
        
        # Сохранение в csv
        if all_links:
            df = pd.DataFrame({'Product Links': all_links})
            tfile = open(OUTPUT_FILE_NAME+'.csv','w', encoding="utf-8")
            tfile.write(df.to_string(header=False, index=False))
            tfile.close()

            print(f"Ссылки успешно сохранены в {OUTPUT_FILE_NAME}")
            print(f"Всего найдено ссылок: {len(all_links)}")
        else:
            print("Не удалось извлечь ссылки на продукты")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()