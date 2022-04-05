from datetime import datetime, timedelta
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager

class DateAttributeError(Exception):
    pass

def extract_url_dl(no_browser=True, start_date=datetime(2016, 3, 30), end_date=datetime(2016, 4, 3)) -> {}:
    """
    Extract the last time of the BERA's publication (needed to generate the download url)
    ---
    Return
    [
    'MONT-BLANC.20160330130701',
    ...
    ]
    """
    url_dls = []
    if start_date > end_date:
        raise DateAttributeError

    firefox_options = Options()
    if no_browser:
        firefox_options.add_argument("--headless")

    url_time_publishment = "https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50"
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=firefox_options)

    # Load the page, accept cookies and click on the download section
    driver.get(url_time_publishment)
    driver.implicitly_wait(3)
    driver.find_element(By.XPATH, "//input[@type='submit' and @value='Accepter']").click()
    driver.find_elements(By.CSS_SELECTOR, ".telechargements")[3].click()

    datepicker = driver.find_element(By.ID, 'datepicker')
    i = start_date
    while i <= end_date:
        from selenium.webdriver.common.keys import Keys
        datepicker.send_keys(Keys.CONTROL + "a")
        datepicker.send_keys(i.strftime("%Y%m%d"))
        driver.find_element(By.ID, 'select_massif').click()
        massifs = driver.find_element(By.ID, 'select_massif').find_elements(By.XPATH, '//option')
        for option in massifs:
            option.click()
            datetime_publication = driver.find_elements(By.ID, 'select_heures')[-1].get_attribute('value')
            url_dls.append(f"{option.text}.{datetime_publication}")
            # if option.text == "CHABLAIS":  # Stopping here. Other elements are unvalid options. How to better filter my list ?
            if option.text == "CAPCIR-PUYMORENS":  # Stopping here. Other elements are unvalid options. How to better filter my list ?
                break
        i = i + timedelta(days=1)

    driver.close()
    # with open('data/urls_list.txt', 'w') as f:
    #     url_dls = map(lambda x:x+'\n', url_dls)
    #     f.writelines(url_dls)
    return '\n'.join(map(lambda x:str(x), url_dls))



if __name__ == '__main__':
    pdfs = extract_url_dl(no_browser=False, start_date=datetime(2016, 4, 1), end_date=datetime(2016, 4, 1))
