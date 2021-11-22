from selenium.webdriver.opera.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from time import sleep

UTF_8 = "utf-8"
FILE_NAME = "crontab.tab"

CRONTAB_WEB_SITE_URL = "https://crontab.guru"

CRONTAB_JOB_COUNT = 100
MAX_ITER_COUNT = 1000
CRONTAB_JOB_STRING = "{} echo {};\n"

XPATH_TO_RANDOM_BUTTON = "//*[contains(text(), 'random')]"
CRONTAB_TIME_ELEMENT_ID = "input"
CRONTAB_TIME_HUMAN_READABLE_ID = "hr"


def generate_random_crontab_string(driver: WebDriver):
    button: WebElement = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, XPATH_TO_RANDOM_BUTTON))
    )
    button.click()


def get_human_readable_element(driver: WebDriver) -> WebElement:
    return driver.find_element(By.ID, CRONTAB_TIME_HUMAN_READABLE_ID)


def get_crontab_job_time(driver: WebDriver) -> WebElement:
    return driver.find_element(By.ID, CRONTAB_TIME_ELEMENT_ID)


def init() -> WebDriver:
    return webdriver.Chrome(executable_path=ChromeDriverManager().install())


def workflow(driver: WebDriver):
    generate_random_crontab_string(driver)
    crontab_jobs = set()
    crontab_job_number = 0
    curr_iter = 0

    while crontab_job_number < CRONTAB_JOB_COUNT and curr_iter < MAX_ITER_COUNT:
        generate_random_crontab_string(driver)
        time: str = get_crontab_job_time(driver).get_attribute("value")
        text: str = get_human_readable_element(driver).text

        number_of_crontab_jobs_before = len(crontab_jobs)
        crontab_jobs.add(CRONTAB_JOB_STRING.format(time, text))
        number_of_crontab_jobs_after = len(crontab_jobs)

        if number_of_crontab_jobs_before == number_of_crontab_jobs_after:
            crontab_job_number -= 1

        crontab_job_number += 1
        curr_iter += 1

        sleep(0.1)
    with open(FILE_NAME, "w+", encoding=UTF_8) as crontab_file:
        for crontab_job in crontab_jobs:
            crontab_file.write(crontab_job)


if __name__ == "__main__":
    chrome_driver: WebDriver = init()
    chrome_driver.get(CRONTAB_WEB_SITE_URL)

    try:
        workflow(chrome_driver)
    except Exception as exc:
        print(exc)

    chrome_driver.stop_client()
    chrome_driver.close()
    chrome_driver.quit()
