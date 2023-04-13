import time
import os 

import RoomCapacities
from RoomSettings import intializeRoomSettings, FAVORITE_TIMES_MW, FAVORITE_TIMES_TTH, FAVORITE_DATES, FAVORITE_ROOMS

from queue import PriorityQueue
from datetime import datetime, timedelta

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoAlertPresentException

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options

import pytz

load_dotenv()
os.environ["PATH"] += os.pathsep + '/usr/local/bin'
#chrome_service = ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())

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

driver = webdriver.Chrome(options=chrome_options)
print(driver.capabilities['browserName'])
print(driver.capabilities['browserVersion'])

optimalRooms = PriorityQueue()

def main():
    driver.maximize_window()
    #driver.get('https://cpp.libcal.com/reserve/study-rooms')
    print("hi")
    # Add some elements to the queue
    #print(optimalRooms.empty())
    #table()
    bookForWeek(optimalRooms)
    #findOptimalRoom(getAvailableRooms())
    # print(optimalRooms.get()[6].get_attribute('title'))
    #optimalRoom = optimalRooms.get()[6]
    #print(optimalRoom.get_attribute('title'))
    #selectRoom(optimalRoom)
    #login()
    #duo2Factor()
    #confirm()
    #driver.close()

def bookForWeek(optimalRooms):
    newBookings = []
    with open("RoomBookings.txt", "r") as f:
            lines = f.readlines()
    for i in range(0, len(FAVORITE_DATES)):
        print("runningg")
        otherBookingChoices = []
        clickedNextPage = False
        dateMDY = FAVORITE_DATES[i] #(FAVORITE_DATES[i].split(',')[1] + FAVORITE_DATES[i].split(',')[1])[1:]
        dayOfWeek = datetime.strptime(dateMDY, "%B %d, %Y")
        dayOfWeek = dayOfWeek.strftime("%A")
        print(dateMDY)
        print(dayOfWeek)
        if any(FAVORITE_DATES[i] in line for line in lines):
            print("ALREADY BOOKED!!!!!!!!!")
            continue
        else:
            driver.get('https://cpp.libcal.com/reserve/study-rooms')
            datesOnPage = getDatesInTable()
            print(datesOnPage)
            #print(FAVORITE_DATES[i])
            if (dayOfWeek + ", " + dateMDY) not in datesOnPage:
                print("not in table")
                clickedNextPage = True
                while (dayOfWeek + ", "+ dateMDY) not in datesOnPage:
                    print("testtt")
                    if not nextPage():
                        break
                    datesOnPage = getDatesInTable()
                    print(dateMDY)
                    print(datesOnPage)
            #FAVORITE_DATES.pop(0)
            #book room logic here
            optimalRooms = PriorityQueue()
            availableRooms = getAvailableRooms(dayOfWeek)
            if len(availableRooms) == 0:
                print("NO ROOMS!!!!!!!!!!!!")
                continue
            optimalRoom = findOptimalRoom(optimalRooms, availableRooms)
            print("hereeeeeeeeeeeeeeeeeeeee")
            print(optimalRooms.empty())
            #optimalRoom = optimalRooms.get()
            optimalRoomData = optimalRoom[6].get_attribute('title')
            print(optimalRoomData)
            #print(optimalRoom.get_attribute('title'))
            print("22222222222222222222")
            while not optimalRooms.empty():
                room = optimalRooms.get()
                roomEndTime = (room[7].strftime("%I:%M%p")).lower()
                if roomEndTime[0] == "0":
                    roomEndTime = roomEndTime[1:]
                otherBookingChoices.append(room[6].get_attribute('title') + " till " + roomEndTime + "\n")
            otherBookingChoices.append("\n")
            # optimalRoom = optimalRooms.get()[6]
            # print(optimalRoom.get_attribute('title'))
            selectRoom(optimalRoom[6])
            login()
            duo2Factor()
            confirm()

            roomEndTime = (optimalRoom[7].strftime("%I:%M%p")).lower()
            if roomEndTime[0] == "0":
                roomEndTime = roomEndTime[1:]
            newBookings.append((optimalRoomData + " till " + roomEndTime))
            # with open("OtherBookingChoices.txt", "a") as f:
            #     f.writelines(otherBookingChoices)
            # while (room[0] == i)and not optimalRooms.empty():
            #     room = optimalRooms.get()
                #print(room[6].get_attribute('title'))
            #optimalRooms.put(room)
            print(optimalRooms.empty())
            #print(optimalRooms.get()[6].get_attribute('title'))
            # print(optimalRooms.get()[6].get_attribute('title'))
            # print(optimalRooms.get()[6].get_attribute('title'))
            # print(optimalRooms.get()[6].get_attribute('title'))

    saveToFile(newBookings)

def nextPage():
    nextButton = driver.find_element(by=By.XPATH, value="//*[@id='eq-time-grid']/div[1]/div[1]/div/button[2]")
    if not nextButton.is_enabled():
        return False
    nextButton.click()
    time.sleep(1)
    return True

def saveToFile(newBookings):
    print("file changes now")
    with open("RoomBookings.txt", "r") as f:
        lines = f.readlines()
    
    now = datetime.now()
    pst_timezone = pytz.timezone('US/Pacific')
    now = now.astimezone(pst_timezone)
    now = now.strftime("%B %d, %Y")
    nowDate = datetime.strptime(now, "%B %d, %Y")

    newLines = []
    for roomInfo in lines:
        date_part = roomInfo.split("-")[0]
        date_part = date_part[date_part.index(',')+2:len(date_part)-1]
        roomDate = datetime.strptime(date_part, "%B %d, %Y")
        if nowDate <= roomDate:
            newLines.append(roomInfo)

    with open('RoomBookings.txt', 'w') as f:
        f.writelines(newLines)

    with open("RoomBookings.txt", "a") as f:
        #newBookings = ["hi", "michael", "i like", "piiza"]
        for i in range(len(newBookings)):
            newBookings[i] = newBookings[i] + "\n"
        f.writelines(newBookings)

def getDatesInTable():
    try:
        alert = driver.switch_to.alert
        alert.dismiss()
        driver.switch_to.default_content() # switch back to the browser
    except NoAlertPresentException:
        print("no alert")
    except Exception as e:
        print("got an error:" + str(e))
    
    try:
        time.sleep(2)
        tableDates = driver.find_elements(by=By.XPATH, value="//*[@id='eq-time-grid']/div[2]/div/table/thead/tr/td[3]/div/div/div/table/tbody/tr[1]/th/div/span")
        print(tableDates[0].text)
        print(tableDates[1].text)
        print(tableDates[2].text)
        return [tableDates[0].text, tableDates[1].text, tableDates[2].text]
    except Exception as e:
        print("oh noooo")
        print(str(e))


def getAvailableRooms(dayOfWeek):
    #table = driver.find_element(by=By.XPATH, value="")
    print("hiiiiiiiiiiiii")
    print(dayOfWeek)
    time.sleep(2)
    allRooms = driver.find_elements(by=By.CLASS_NAME, value='fc-timeline-event')
    print(len(allRooms))
    avalibleRooms = list(filter(removeUnvailableRoom, allRooms))
    avalibleRooms_same_day = list()
    for room in avalibleRooms:
        if dayOfWeek in room.get_attribute('title'):
            avalibleRooms_same_day.append(room)
    # for room in amt:
    #     date = room.get_attribute('title')
    #     if len(date) != 0:
    #         green.append(room)
    print(len(avalibleRooms))
    print(len(avalibleRooms_same_day))
    # for room in avalibleRooms:
    #     date = room.get_attribute('title')
    #     print(date)
    return avalibleRooms_same_day

def findOptimalRoom(optimalRooms, rooms):
    print("hi")
    optimalRoom = (100,100,100,100,100,100,100,100)
    rooms = set(rooms)

    now = datetime.now()
    pst_timezone = pytz.timezone('US/Pacific')
    now = now.astimezone(pst_timezone)
    next_day = now + timedelta(days=1)
    currentDate = next_day.strftime("%B %d, %Y")
    currentDayOfWeek = next_day.strftime("%A")
    #print(currentDayOfWeek)
    
    availableRooms = set()
    for room in rooms: 
        roomInfo = room.get_attribute('title')
        availableRooms.add(roomInfo)
        #print(roomInfo)

    roomCount = 0
    for room in rooms:
        #11:30am Wednesday, December 21, 2022 - 5929 - Available
        roomInfo = room.get_attribute('title')
        #print(roomInfo)
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
        roomDayOfWeek = roomInfo.split(',')[0].split(" ")[1]
        roomDayOfWeek = roomDayOfWeek.strip()
        #print(currentTime)

        #print(roomTime)
        intervalsOf30Min = 1
        time = datetime.strptime(roomTime, "%I:%M%p")
        for i in range(5):
            #time = datetime.strptime(roomTime, "%I:%M%p")

            time += timedelta(minutes=30)
            roomEndTime = time.strftime("%I:%M%p")
            roomEndTime = roomEndTime.lower()
            if roomEndTime[0] == "0":
                roomEndTime = roomEndTime[1:]
            roomData = ''.join([roomEndTime, " ", roomDateAndNumber])
            #print("this is room data:" + roomData + "L")
            print(roomData)
            #print(availableRooms)
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
        #print(roomNumber)
        if roomDayOfWeek == "Monday" or roomDayOfWeek == "Wednesday":
            if roomTime not in FAVORITE_TIMES_MW:
                timeScore = len(FAVORITE_TIMES_MW)
            else:
                timeScore = FAVORITE_TIMES_MW.index(roomTime)
        elif roomDayOfWeek == "Tuesday" or roomDayOfWeek == "Thursday":
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

        #optimalRooms.put((dateScore, timeScore , allotedTimeScore, roomScore, capacityScore, roomCount, room, time))
        optimalRoom = min((dateScore, timeScore , allotedTimeScore, roomScore, capacityScore, roomCount, room, time), optimalRoom)
        #print(optimalRooms.empty())
        roomCount+=1
        #print(roomDate)


    print()
    now = datetime.now()

    # Add 1 day to the current date
    next_day = now + timedelta(days=1)

    # Print the next day's date in the format "Month Day, Year"
    #print(next_day.strftime("%B %d, %Y"))

    time = datetime.strptime("10:30am", "%I:%M%p")

    # Add 30 minutes
    time += timedelta(minutes=30)

    # New time: 11:00am
    #print(time.strftime("%I:%M%p"))
    
    return optimalRoom


def removeUnvailableRoom(room):
    date = room.get_attribute('title')
    if len(date) == 0:
        return False
    if "Unavailable" in date:
        return False
    return True

def selectRoom(optimalRoom):
    print(driver.title)
    print("selecting room!")
    time.sleep(1)
    # roomSelection = driver.find_element(by=By.XPATH, value="//*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[14]/td/div/div[2]/div[13]/a")
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[29]/td/div/div[2]/div[7]/a/div/div/div
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[33]/td/div/div[2]/div[5]/a
    print(optimalRoom.get_attribute('title'))
    print("----------------------------------------------")
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
    try:
        inputUsername = driver.find_element(by=By.XPATH, value="//*[@id='username']")
        inputUsername.send_keys(os.environ.get("CPP_USERNAME"))
        inputPassword = driver.find_element(by=By.XPATH, value="//*[@id='password']")
        inputPassword.send_keys(os.environ.get("CPP_PASSWORD"))
        loginButton = driver.find_element(by=By.XPATH, value="//*[@id='formcontainer']/form/button")
        loginButton.click()
    except:
        print("Already logged in")

def duo2Factor():
    time.sleep(2)
    try:
        driver.switch_to.frame(driver.find_element(by=By.TAG_NAME, value='iframe'))
        sendPushButton = driver.find_element(by=By.XPATH, value="//*[@id='auth_methods']/fieldset/div[1]/button")
        sendPushButton.click()
    except:
        print("Already logged in")
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
    #test()
