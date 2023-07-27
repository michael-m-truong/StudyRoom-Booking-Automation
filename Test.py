from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime, timedelta
import time

import pytz

def get_pst_time():
    # Get the current time in UTC
    utc_now = datetime.utcnow()
    print(utc_now)
    
    # Define the PST time zone
    pst = pytz.timezone('US/Pacific')
    
    # Convert the current UTC time to PST
    pst_now = utc_now.astimezone(pst)
    return pst_now

def get_seconds_to_next_pst_midnight():
    # Get the current PST time
    pst_now = get_pst_time()
    
    # Calculate the time until the next midnight (12 AM) in PST
    next_midnight = pst_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    time_difference = next_midnight - pst_now
    
    # Convert the time difference to seconds
    seconds_to_wait = time_difference.total_seconds()
    return seconds_to_wait


options = webdriver.ChromeOptions()
#options.add_experimental_option('excludeSwitches', ['enable-logging'])  
x=Service('C:\Program Files (x86)\chromedriver.exe')
#options.headless = True
driver = webdriver.Chrome(service=x, options=options)
driver.maximize_window()

driver.get('https://cpp.libcal.com/reserve/study-rooms')


wait = WebDriverWait(driver, 10)
button_xpath = '//*[@id="eq-time-grid"]/div[1]/div[1]/button[1]'
button = wait.until(EC.element_to_be_clickable((By.XPATH, button_xpath)))

# Click the button
button.click()


# Wait for the table to be present
wait = WebDriverWait(driver, 10)
#table_xpath = '//*[@id="equip_"]/div[5]/div[1]/table/tbody'
#table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))

# Unfocus the clicked button using JavaScript
tooltip = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "tooltip")))
driver.execute_script("arguments[0].remove();", tooltip)


# Get the current date in UTC
utc_now = datetime.utcnow()

# Convert to Greenwich Mean Time (GMT)
gmt_tz = pytz.timezone('GMT')
gmt_now = utc_now.astimezone(gmt_tz)

# Calculate the date one week in advance in GMT
gmt_one_week_in_advance = gmt_now + timedelta(days=6)

# Set the time to 00:00:00 for both dates
gmt_today_date = gmt_now.replace(hour=0, minute=0, second=0, microsecond=0)
gmt_one_week_in_advance_date = gmt_one_week_in_advance.replace(hour=0, minute=0, second=0, microsecond=0)

# Convert dates to Unix timestamps in milliseconds
today_unix_ms = int(gmt_today_date.timestamp()) * 1000
one_week_in_advance_unix_ms = int(gmt_one_week_in_advance_date.timestamp()) * 1000

print(today_unix_ms)
print(one_week_in_advance_unix_ms)

# Find the "today" day element in the table
today_element_xpath = f'//td[@data-date="{today_unix_ms}"]'
today_element = wait.until(EC.element_to_be_clickable((By.XPATH, today_element_xpath)))


# Find the "1 week in advance" day element in the table
one_week_in_advance_element_xpath = f'//td[@data-date="{one_week_in_advance_unix_ms}"]'
one_week_in_advance_element = wait.until(EC.element_to_be_clickable((By.XPATH, one_week_in_advance_element_xpath)))



#wait till midnight
# seconds_to_wait = get_seconds_to_next_pst_midnight()
# print(f"Waiting {seconds_to_wait} seconds until midnight PST.")
# time.sleep(seconds_to_wait)

# Unfocus the clicked button using JavaScript
#driver.execute_script("arguments[0].blur();", button)

# Click on the "1 week in advance" day element
one_week_in_advance_element.click()


test = f'//*[@id="eq-time-grid"]/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[29]/td/div/div[2]/div[6]/a'
bestRoom = wait.until(EC.element_to_be_clickable((By.XPATH, test)))
driver.execute_script("arguments[0].scrollIntoView();", bestRoom)
bestRoom.click()
# submitTime = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit_times']")))
# driver.execute_script("arguments[0].scrollIntoView();", submitTime)
# submitTime.click()

# time.sleep(3)
# driver.get('https://cpp.libcal.com/reserve/study-rooms')

time.sleep(100000)


#  XPATH FOR 4134 10AM
# //*[@id="eq-time-grid"]/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[29]/td/div/div[2]/div[6]/a