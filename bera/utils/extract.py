import logging

from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import ElementNotInteractableException, StaleElementReferenceException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager
from collections import defaultdict


class DateAttributeError(Exception):
    pass


def accept_eventual_cookies(driver):
    driver.implicitly_wait(3)
    try: # In case the website asks to valide cookies for the session
        driver.find_element(By.XPATH, "//input[@type='submit' and @value='Accepter']").click()
    except NoSuchElementException:
        pass


def extract_url_dl(no_browser=True, start_date=datetime(2016, 3, 30), end_date=datetime(2016, 4, 3)) -> {}:
    """
    Extract the last time of the BERA's publication (needed to generate the download url)
    ---
    Return
    {
    'MONT-BLANC': '20160330130701',
    ...
    }
    """
    url_dls = defaultdict(list)
    if start_date > end_date:
        raise DateAttributeError
    # if not start_date.isinstance(datetime):
    #     raise DateAttributeError

    firefox_options = Options()
    if no_browser:
        firefox_options.add_argument("--headless")

    url_time_publishment = "https://donneespubliques.meteofrance.fr/?fond=produit&id_produit=265&id_rubrique=50"
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=firefox_options)

    # Load the page, accept cookies and click on the download section
    driver.get(url_time_publishment)

    accept_eventual_cookies(driver)

    driver.find_elements(By.CSS_SELECTOR, ".telechargements")[3].click()

    datepicker = driver.find_element(By.ID, 'datepicker')
    i = start_date
    while i <= end_date:
        logging.info(i)
        from selenium.webdriver.common.keys import Keys
        datepicker.send_keys(Keys.CONTROL + "a")
        datepicker.send_keys(i.strftime("%Y%m%d"))
        driver.find_element(By.ID, 'select_massif').click()

        select_massif = Select(driver.find_element(By.ID,'select_massif'))

        for massif in select_massif.options:
            try:
                massif.click()
            except StaleElementReferenceException:
                break
            except ElementNotInteractableException:
                break
            datetime_publication = driver.find_elements(By.ID, 'select_heures')[-1].get_attribute('value')
            url_dls[massif.text.replace('/', '_')].append(datetime_publication)

        i = i + timedelta(days=1)

    driver.close()
    return url_dls


if __name__ == '__main__':
    pdfs = extract_url_dl(no_browser=False, start_date=datetime(2018, 4, 1), end_date=datetime(2018, 4, 1))
    print(pdfs)
