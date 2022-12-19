import time
import os 

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType
from selenium.webdriver.chrome.options import Options


load_dotenv()
chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

chrome_options = Options()
options = [
    "--headless",
    "--disable-gpu",
    "--window-size=1920,1200",
    "--ignore-certificate-errors",
    "--disable-extensions",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]
for option in options:
    chrome_options.add_argument(option)

driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

def main():
    driver.maximize_window()
    driver.get('https://cpp.libcal.com/reserve/study-rooms')
    selectRoom()
    login()
    duo2Factor()
    confirm()
    #driver.close()

def selectRoom():
    print(driver.title)
    time.sleep(1)
    roomSelection = driver.find_element(by=By.XPATH, value="//*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[20]/td/div/div[2]/div[4]/a/div/div/div")
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[29]/td/div/div[2]/div[7]/a/div/div/div
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[33]/td/div/div[2]/div[5]/a
    driver.execute_script("arguments[0].scrollIntoView();", roomSelection)
    roomSelection.click()
    print("test")
    time.sleep(1)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    submitTime = driver.find_element(by=By.XPATH, value="//*[@id='submit_times']")
    driver.execute_script("arguments[0].scrollIntoView();", submitTime)

    submitTime.click()
    time.sleep(1)

def login():
    time.sleep(1)
    inputUsername = driver.find_element(by=By.XPATH, value="//*[@id='username']")
    inputUsername.send_keys(os.environ.get("CPP_USERNAME"))
    inputPassword = driver.find_element(by=By.XPATH, value="//*[@id='password']")
    inputPassword.send_keys(os.environ.get("CPP_PASSWORD"))
    loginButton = driver.find_element(by=By.XPATH, value="//*[@id='formcontainer']/form/button")
    loginButton.click()

def duo2Factor():
    time.sleep(2)
    driver.switch_to.frame(driver.find_element(by=By.TAG_NAME, value='iframe'))
    sendPushButton = driver.find_element(by=By.XPATH, value="//*[@id='auth_methods']/fieldset/div[1]/button")
    sendPushButton.click()
    #driver.switch_to.default_content() #

def confirm():
    print("here")
    try:
        continueButton = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='terms_accept']"))
        )
        continueButton.click()

        confirmButton = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='s-lc-eq-bform-submit']"))
        )
        confirmButton.click()
        print("clicked")
    except:
        print("what")
        driver.quit()
    print("done")

if __name__ == "__main__":
    main()