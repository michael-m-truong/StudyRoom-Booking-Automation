import time
import os 
import re

from queue import PriorityQueue
#import datetime
from datetime import datetime, timedelta

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
options = webdriver.ChromeOptions()
#options.add_experimental_option('excludeSwitches', ['enable-logging'])  
x=Service('C:\Program Files (x86)\chromedriver.exe')
options.headless = True
driver = webdriver.Chrome(service=x, options=options)

def getDaysOfWeek():
    days = []
    for i in range(1,14):
        now = datetime.now()
        next_day = now + timedelta(days=i)
        currentDate = next_day.strftime("%B %d, %Y")
        days.append(currentDate)
    return days   

days = getDaysOfWeek()
print(days)
FAVORITE_TIMES_MW = ["10:00am", "10:30am"]
FAVORITE_TIMES_TTH = ["2:30pm", "3:00pm"]
FAVORITE_ROOMS = ["4134", "4823", "4136", "6919A"]
FAVORITE_DATES = [days[0], days[1], days[2], days[3], days[4]]   #day[0] is tomorrow, day[1] 1 day after tom, etc.

optimalRooms = PriorityQueue()
# (date, time, room)


def main():
    driver.maximize_window()
    driver.get('https://cpp.libcal.com/reserve/study-rooms')
    findOptimalRoom(getAvailableRooms())
    #selectRoom()
    #login()
    #duo2Factor()
    #confirm()
    #driver.close()


def getAvailableRooms():
    #table = driver.find_element(by=By.XPATH, value="")
    time.sleep(2)
    allRooms = driver.find_elements(by=By.CLASS_NAME, value='fc-timeline-event')
    print(len(allRooms))
    avalibleRooms = list(filter(removeUnvailableRoom, allRooms))
    # for room in amt:
    #     date = room.get_attribute('title')
    #     if len(date) != 0:
    #         green.append(room)
    print(len(avalibleRooms))
    # for room in avalibleRooms:
    #     date = room.get_attribute('title')
    #     print(date)
    return avalibleRooms

def findOptimalRoom(rooms):
    rooms = set(rooms)

    now = datetime.now()

    next_day = now + timedelta(days=1)
    currentDate = next_day.strftime("%B %d, %Y")
    currentDayOfWeek = next_day.strftime("%A")
    print(currentDayOfWeek)
    
    availableRooms = set()
    for room in rooms: 
        roomInfo = room.get_attribute('title')
        availableRooms.add(roomInfo)
        print(roomInfo)

    for room in rooms:
        roomInfo = room.get_attribute('title')
        # Find the index of the "am" or "pm" substring
        index = roomInfo.index("am") if "am" in roomInfo else roomInfo.index("pm")

        # Slice the string starting from the index of the "am" or "pm" substring
        roomTime = roomInfo[:index+2]
        indexes = [index for index, char in enumerate(roomInfo) if char == '-']
        roomNumber = roomInfo[indexes[0]+1:indexes[1]-1]
        date_part = roomInfo.split("-")[0]
        date_part = date_part[date_part.index(',')+2:len(date_part)-1]
        roomDate = date_part
        roomDateAndNumber = roomInfo[index+3:]
        #print(currentTime)

        print(roomTime)
        intervalsOf30Min = 1
        for i in range(5):
            time = datetime.strptime(roomTime, "%I:%M%p")

            time += timedelta(minutes=30)
            roomTime = time.strftime("%I:%M%p")
            roomTime = roomTime.lower()
            if roomTime[0] == "0":
                roomTime = roomTime[1:]
            roomData = ''.join([roomTime, " ", roomDateAndNumber])
            print("this is room data:" + roomData + "L")
            if roomData in availableRooms:
                intervalsOf30Min+=1
            else:
                break
        print("intervalsOf30Min: " + str(intervalsOf30Min))
        roomScore = 0
        timeScore = 0
        dateScore = 0
        if currentDayOfWeek == "Monday" or currentDayOfWeek == "Wednesday":
            if roomTime not in FAVORITE_TIMES_MW:
                timeScore = len(FAVORITE_TIMES_MW)
            else:
                timeScore = FAVORITE_TIMES_MW.index(roomTime)
        elif currentDayOfWeek == "Tuesday" or currentDayOfWeek == "Thursday":
            if roomTime not in FAVORITE_TIMES_TTH:
                timeScore = len(FAVORITE_TIMES_TTH)
            else:
                timeScore = FAVORITE_TIMES_TTH.index(roomTime)
        # need to do else logic for other days of week
        if roomDate not in FAVORITE_DATES:
            dateScore = len(FAVORITE_DATES)
        else:
            dateScore = 0
        optimalRooms.put(())
        print(roomDate)


    print()
    now = datetime.now()

    # Add 1 day to the current date
    next_day = now + timedelta(days=1)

    # Print the next day's date in the format "Month Day, Year"
    print(next_day.strftime("%B %d, %Y"))

    time = datetime.strptime("10:30am", "%I:%M%p")

    # Add 30 minutes
    time += timedelta(minutes=30)

    # New time: 11:00am
    print(time.strftime("%I:%M%p"))


def removeUnvailableRoom(room):
    date = room.get_attribute('title')
    #print("hi")
    if len(date) == 0:
        return False
    if "Unavailable" in date:
        return False
    return True

def selectRoom():
    print(driver.title)
    time.sleep(1)
    roomSelection = driver.find_element(by=By.XPATH, value="//*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[14]/td/div/div[2]/div[4]/a/div/div/div")
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