import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Настройки
# TEST_TARGET_URL = "https://catalogue.ite-expo.ru/ru-RU/specialpages/exhibitor_view.aspx?project_id=536&exhibitor_id=90442&itemid=138777"
# https://catalogue.ite-expo.ru/ru-RU/exhibitorlist.aspx?project_id=536
OUTPUT_FILE = "scpr_ee2025_exh_data.csv" # сырые данные
PAGES_TO_SCRAPE = 9  # Сколько страниц каталога обработать 
EXH_FILE = "scrp_ee2025_exh.csv" # Шаблон для заполнения
RESULT_FILE = "scrp_ee2025_exh_result.csv" # Заполненный шаблон

def init_driver():
    """Инициализация веб-драйвера с настройками"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def scrape_exhibitor_data(driver, url):
    """Сбор данных со страницы экспонента"""
    try:
        driver.get(url)
        
        # Ожидаем загрузки основных элементов
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".scorecard")) #".exhibitor-header"))
        )
        
        data = []
        data_shift = 0
        try:
            data.append(driver.find_element(By.XPATH, '//*[@id="frameContent"]/div/div[1]').text.strip())
        except Exception as e:
            data.append("-")
        try:
            if driver.find_element(By.XPATH, '//*[@id="frameContent"]/div/div[3]').text.strip() == "":
                data_shift = 1
            data.append(driver.find_element(By.XPATH, '//*[@id="frameContent"]/div/div['+str(3-data_shift)+']').text.strip())
        except Exception as e:
            data.append("-")
        try:
            data.append(driver.find_element(By.XPATH,  '//*[@id="frameContent"]/div/div['+str(5-data_shift)+']/div').text.strip())
        except Exception as e:
            data.append("-")
        try:
            data.append(driver.find_element(By.XPATH,  '//*[@id="frameContent"]/div/div['+str(6-data_shift)+']/div').text.strip())
        except Exception as e:
            data.append("-")
        try:
            data.append(driver.find_element(By.XPATH,  '//*[@id="frameContent"]/div/div['+str(7-data_shift)+']/div').text.strip())
        except Exception as e:
            data.append("-")
        try:
            data.append(driver.find_element(By.XPATH,  '//*[@id="frameContent"]/div/div['+str(8-data_shift)+']/div').text.strip())
        except Exception as e:
            data.append("-")
        try:
            data.append(driver.find_element(By.XPATH,  '//*[@id="frameContent"]/div/div['+str(9-data_shift)+']').text.replace('Бренды\n', '').strip())
        except Exception as e:
            data.append("-")

        return data
    
    except Exception as e:
        print(f"Ошибка при сборе данных: {str(e)}")
        return None

def main():
    driver = init_driver()
    all_links = []

    try:
        print("Сбор данных")
        
        # Приём цу
        dfi = pd.read_csv(EXH_FILE, header=None, sep=";")
        dfi = dfi.astype('object')
        page_num = 1
        TARGET_URL = dfi[0][page_num-1]

        # Сбор данных
        while TARGET_URL:

            print(f"Обработка страницы {page_num}: {TARGET_URL}")
            company_links = scrape_exhibitor_data(driver, TARGET_URL)
            all_links.append(company_links)
            print(f"Обработано: {len(all_links)}")

            # Дополняем входной DataFrame
            dfi.loc[page_num-1,3] = company_links[0]
            dfi.loc[page_num-1,4] = company_links[1]
            dfi.loc[page_num-1,6] = company_links[2]
            dfi.loc[page_num-1,7] = company_links[3]
            dfi.loc[page_num-1,8] = company_links[4]
            dfi.loc[page_num-1,9] = company_links[5]
            dfi.loc[page_num-1,11] = company_links[6]

            # Проверяем лимит страниц
            if PAGES_TO_SCRAPE and page_num >= len(dfi[0]): # PAGES_TO_SCRAPE: #
                break

            # Переходим на следующую страницу
            page_num += 1
            TARGET_URL = dfi[0][page_num-1]

            # Случайная задержка между запросами
            time.sleep(random.uniform(1, 3))



        if all_links:
            # Сохранение результатов
            df = pd.DataFrame(all_links)
            df.to_csv(OUTPUT_FILE, header=False, index=False, sep=';')
            dfi.to_csv(RESULT_FILE, header=False, index=False, sep=';')

        else:
            print("Не удалось собрать данные")
    
    finally:
        driver.quit()
        print("Работа завершена")

if __name__ == "__main__":
    main()