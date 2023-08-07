import time
import os 
import threading

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
from selenium.webdriver.common.action_chains import ActionChains


#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.core.utils import ChromeType
from selenium.webdriver.chrome.options import Options

import pytz

from Util import get_pst_time, get_seconds_to_next_pst_midnight

#load_dotenv()
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

wait = WebDriverWait(driver, 10)

def main():
    driver.maximize_window()
    #driver.get('https://cpp.libcal.com/reserve/study-rooms')
    print("hi")
    # Add some elements to the queue
    #print(optimalRooms.empty())
    #table()
    upToDate = saveToFile([])
    if upToDate:
        goToLogin()
        login()
        duo2Factor()
        driver.get('https://cpp.libcal.com/reserve/study-rooms')
        ROOM_4134, room_title = getRoomFirst()
        login() # some rzn i need this
        selectRoom(ROOM_4134)
        login() #not if need this but if do  may need duo fac too?
        duo2Factor()
        roomEndTime = confirm()
        
        newBooking = []
        newBooking.append((room_title + " till " + roomEndTime))
        saveToFile(newBooking)

    else:
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

def goToLogin():
    driver.get('https://my.cpp.edu')

def getRoomFirst():
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
    gmt_one_week_in_advance = gmt_now + timedelta(days=4)  #when testing make days < 7

    # Set the time to 00:00:00 for both dates
    gmt_today_date = gmt_now.replace(hour=0, minute=0, second=0, microsecond=0)
    gmt_one_week_in_advance_date = gmt_one_week_in_advance.replace(hour=0, minute=0, second=0, microsecond=0)

    # Convert dates to Unix timestamps in milliseconds
    today_unix_ms = int(gmt_today_date.timestamp()) * 1000
    one_week_in_advance_unix_ms = int(gmt_one_week_in_advance_date.timestamp()) * 1000

    print(today_unix_ms)
    print(one_week_in_advance_unix_ms)

    # Find the "today" day element in the table
    # today_element_xpath = f'//td[@data-date="{today_unix_ms}"]'
    # today_element = wait.until(EC.element_to_be_clickable((By.XPATH, today_element_xpath)))

    # Find the "1 week in advance" day element in the table
    one_week_in_advance_element_xpath = f'//td[@data-date="{one_week_in_advance_unix_ms}"]'
    one_week_in_advance_element = wait.until(EC.element_to_be_clickable((By.XPATH, one_week_in_advance_element_xpath)))

    # Create a thread to simulate activity
    activity_stop_event = threading.Event()
    activity_thread = threading.Thread(target=simulate_activity_thread, args=(driver, activity_stop_event))
    activity_thread.start()

    #wait till midnight
    seconds_to_wait = get_seconds_to_next_pst_midnight()
    print(f"Waiting {seconds_to_wait} seconds until midnight PST.")
    time.sleep(seconds_to_wait)

    # Click on the "today" day element
    #today_element.click()
    activity_stop_event.set()
    activity_thread.join()

    # Click on the "1 week in advance" day element
    one_week_in_advance_element.click()


    bestroom = f'//*[@id="eq-time-grid"]/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[29]/td/div/div[2]/div[6]/a'
    bestRoom_element = wait.until(EC.element_to_be_clickable((By.XPATH, bestroom)))
    # bestRoom = wait.until(EC.element_to_be_clickable((By.XPATH, test)))
    # driver.execute_script("arguments[0].scrollIntoView();", bestRoom)
    # bestRoom.click()
    return (bestRoom_element, bestRoom_element.get_attribute('title'))
    
def simulate_activity(driver, seconds):
    # Perform simulated mouse movements to keep the session alive
    body = driver.find_element_by_tag_name('body')
    
    # Simulate moving the mouse cursor to different positions
    actions = ActionChains(driver)
    actions.move_to_element(body).perform()
    actions.move_by_offset(10, 10).perform()  # Move cursor slightly
    actions.move_by_offset(-10, -10).perform()  # Move cursor back

# Simulate activity in a separate thread
def simulate_activity_thread(driver, stop_event):
    while not stop_event.is_set():
        simulate_activity(driver)
        time.sleep(60)  # Simulate activity every 1 minute

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
    num_previous_lines = len(lines)
    
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
    
    with open("RoomBookings.txt", "r") as f:
        current_lines = f.readlines()
    num_current_lines = len(current_lines)

    print(num_previous_lines)
    print(num_current_lines)

    return num_previous_lines - num_current_lines <= 3  #if true, means you are at most updated bookings 1 week advance

def getDatesInTable():
    # Get the current window handle
    current_window_handle = driver.current_window_handle
    print("current: "+ current_window_handle)
    
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        print("alert text: " + alert.text)
        alert.accept()
        driver.switch_to.default_content() # switch back to the browser
    except NoAlertPresentException:
        print("no alert")
    except Exception as e:
        print("got an error:" + str(e))
        
    # driver.switch_to.window(current_window_handle)
    #print("current: "+ current_window_handle)
    #driver.switch_to.default_content()
    #print("current: "+ current_window_handle)
    
    # Wait for the table to load
    try:
        tableDates = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, "//*[@id='eq-time-grid']/div[2]/div/table/thead/tr/td[3]/div/div/div/table/tbody/tr[1]/th/div/span")))
        print("length is: " + str(len(tableDates)))
        print(tableDates[0].text)
        print(tableDates[1].text)
        print(tableDates[2].text)
        return [tableDates[0].text, tableDates[1].text, tableDates[2].text]
    except Exception as e:
        print("The element doesn't appear in 20 seconds")
        print(e)
        return None


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
            # print(roomData)  # used to print room for debugging
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
    #time.sleep(1)
    # roomSelection = driver.find_element(by=By.XPATH, value="//*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[14]/td/div/div[2]/div[13]/a")
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[29]/td/div/div[2]/div[7]/a/div/div/div
    # //*[@id='eq-time-grid']/div[2]/div/table/tbody/tr/td[3]/div/div/div/table/tbody/tr[33]/td/div/div[2]/div[5]/a
    #print(optimalRoom.get_attribute('title'))
    #print("----------------------------------------------")
    driver.execute_script("arguments[0].scrollIntoView();", optimalRoom)
    optimalRoom.click()
    #time.sleep(1)
    # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    submitTime = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='submit_times']")))
    driver.execute_script("arguments[0].scrollIntoView();", submitTime)

    submitTime.click()
    #time.sleep(5)
    print(driver.title)
    print("room selected!")

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
    time.sleep(1)
    try:
        driver.switch_to.frame(driver.find_element(by=By.TAG_NAME, value='iframe'))

        rememberMeButton_xpath = f'//*[@id="login-form"]/div[2]/div/label/input'
        rememberMeButton = driver.find_element(by=By.XPATH, value=rememberMeButton_xpath)
        rememberMeButton.click()
        time.sleep(1)
        sendPushButton = driver.find_element(by=By.XPATH, value="//*[@id='auth_methods']/fieldset/div[1]/button")
        sendPushButton.click()

        time.sleep(8)
    except:
        print("Already duo factored")
    #driver.switch_to.default_content() #

def confirm():
    print("here")
    print(driver.title)
    endTime = None
    #print(driver.page_source)
    #while (driver.title != 'Booking Details - Library Events - California State Polytechnic University, Pomona'):
        #pass
    #time.sleep(10)
    print(driver.title)
    try:
        continueButton = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='terms_accept']"))
        )
        continueButton.click()
        print("pressed continue")

        confirmButton = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='btn-form-submit']"))
        )
        confirmButton.click()
        print("pressed confirm")

        endTime_element = wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@id="s-lc-public-page-content"]/div/div[1]/dl/dd[5]')))
        endTime = (endTime_element.text).split()[2]
        print("clicked")
    except Exception as e:
        print("what")
        print(driver.title)
        print(e)
        driver.quit()
    print("done")
    print("endtime: " +str(endTime))
    return endTime

if __name__ == "__main__":
    main()
    #test()
