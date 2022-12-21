import time
import os 

import RoomCapacities
from RoomSettings import intializeRoomSettings, FAVORITE_TIMES_MW, FAVORITE_TIMES_TTH, FAVORITE_DATES, FAVORITE_ROOMS

from queue import PriorityQueue
from datetime import datetime, timedelta

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options

import pytz

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

intializeRoomSettings()
optimalRooms = PriorityQueue()

def main():
    driver.maximize_window()
    driver.get('https://cpp.libcal.com/reserve/study-rooms')
    findOptimalRoom(getAvailableRooms())
    optimalRoom = optimalRooms.get()[6]
    print(optimalRoom.get_attribute('title'))
    selectRoom(optimalRoom)
    login()
    duo2Factor()
    confirm()
    #driver.close()

def getAvailableRooms():
    #table = driver.find_element(by=By.XPATH, value="")
    time.sleep(2)
    allRooms = driver.find_elements(by=By.CLASS_NAME, value='fc-timeline-event')
    #print(len(allRooms))
    avalibleRooms = list(filter(removeUnvailableRoom, allRooms))
    # for room in amt:
    #     date = room.get_attribute('title')
    #     if len(date) != 0:
    #         green.append(room)
    #print(len(avalibleRooms))
    # for room in avalibleRooms:
    #     date = room.get_attribute('title')
    #     print(date)
    return avalibleRooms

def findOptimalRoom(rooms):
    rooms = set(rooms)

    now = datetime.now()
    pst_timezone = pytz.timezone('US/Pacific')
    now = now.astimezone(pst_timezone)
    next_day = now + timedelta(days=1)
    currentDate = next_day.strftime("%B %d, %Y")
    currentDayOfWeek = next_day.strftime("%A")
    
    availableRooms = set()
    for room in rooms: 
        roomInfo = room.get_attribute('title')
        availableRooms.add(roomInfo)

    roomCount = 0
    for room in rooms:
        roomInfo = room.get_attribute('title')
        # Find the index of the "am" or "pm" substring
        index = roomInfo.index("am") if "am" in roomInfo else roomInfo.index("pm")

        # Slice the string starting from the index of the "am" or "pm" substring
        roomTime = roomInfo[:index+2]
        indexes = [index for index, char in enumerate(roomInfo) if char == '-']
        roomNumber = roomInfo[indexes[0]+1:indexes[1]-1].strip()
        date_part = roomInfo.split("-")[0]
        date_part = date_part[date_part.index(',')+2:len(date_part)-1]
        roomDate = date_part
        roomDateAndNumber = roomInfo[index+3:]
        #print(currentTime)

        #print(roomTime)
        intervalsOf30Min = 1
        for i in range(5):
            time = datetime.strptime(roomTime, "%I:%M%p")

            time += timedelta(minutes=30)
            roomEndTime = time.strftime("%I:%M%p")
            roomEndTime = roomEndTime.lower()
            if roomEndTime[0] == "0":
                roomEndTime = roomEndTime[1:]
            roomData = ''.join([roomEndTime, " ", roomDateAndNumber])
            #print("this is room data:" + roomData + "L")
            if roomData in availableRooms:
                intervalsOf30Min+=1
            else:
                break
        #print("intervalsOf30Min: " + str(intervalsOf30Min))
        roomScore = 0
        timeScore = 0
        dateScore = 0
        allotedTimeScore = 0
        capacityScore = 0
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
            dateScore = FAVORITE_DATES.index(roomDate)
        if roomNumber not in FAVORITE_ROOMS:
            favoriteFloorValue = 0
            if roomNumber[0] == "2":
                favoriteFloorValue = 4 # worst floor
            elif roomNumber[0] == "3":
                favoriteFloorValue = 1
            elif roomNumber[0] == "4":
                favoriteFloorValue = 0  #best floor
            elif roomNumber[0] == "5":
                favoriteFloorValue = 3
            elif roomNumber[0] == "6":
                favoriteFloorValue = 2
            roomScore = len(FAVORITE_ROOMS)+favoriteFloorValue
        else:
            roomScore = FAVORITE_ROOMS.index(roomNumber)
        if intervalsOf30Min >= 4:
            allotedTimeScore = -6    
        else:
            allotedTimeScore = intervalsOf30Min*-1
        
        capacityScore = RoomCapacities.RoomCapacities[roomNumber]
        capacityScore*=-1

        optimalRooms.put((dateScore, timeScore , allotedTimeScore, roomScore, capacityScore, roomCount, room))
        roomCount+=1
    

def removeUnvailableRoom(room):
    date = room.get_attribute('title')
    if len(date) == 0:
        return False
    if "Unavailable" in date:
        return False
    return True

def selectRoom(optimalRoom):
    #print(driver.title)
    time.sleep(1)
    #roomSelection = driver.find_element(by=By.XPATH, value="//*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[14]/td/div/div[2]/div[13]/a")
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[29]/td/div/div[2]/div[7]/a/div/div/div
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[33]/td/div/div[2]/div[5]/a
    driver.execute_script("arguments[0].scrollIntoView();", optimalRoom)
    optimalRoom.click()
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
    try:
        continueButton = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='terms_accept']"))
        )
        continueButton.click()

        confirmButton = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='s-lc-eq-bform-submit']"))
        )
        confirmButton.click()
        #print("clicked")
    except:
        driver.quit()
    #print("done")

if __name__ == "__main__":
    main()