from datetime import datetime, timedelta
import pytz

def intializeRoomSettings():
    
    days = []
    for i in range(1,14):
        now = datetime.now()
        pst_timezone = pytz.timezone('US/Pacific')
        now = now.astimezone(pst_timezone)
        next_day = now + timedelta(days=i)
        currentDate = next_day.strftime("%B %-d, %Y")
        print(currentDate)
        days.append(currentDate)
    
    FAVORITE_TIMES_MW = ["10:00am", "10:30am"]
    FAVORITE_TIMES_TTH = ["2:30pm", "3:00pm"]
    FAVORITE_ROOMS = ["4134", "3929", "3927", "4823", "4136"]
    FAVORITE_DATES = [days[0], days[1], days[2], days[3], days[4], days[5], days[6], days[7], days[8], days[9], days[10]]   #day[0] is tomorrow, day[1] 1 day after tom, etc.
    MINIMUM_TIME_ALLOTED = 4   # 4 30 min sessions, so 2 hrs
    return (FAVORITE_TIMES_MW, FAVORITE_TIMES_TTH, FAVORITE_ROOMS, FAVORITE_DATES, MINIMUM_TIME_ALLOTED)

favoriteSettings = intializeRoomSettings()

FAVORITE_TIMES_MW = favoriteSettings[0]
FAVORITE_TIMES_TTH = favoriteSettings[1]
FAVORITE_ROOMS = favoriteSettings[2]
FAVORITE_DATES = favoriteSettings[3]
MINIMUM_TIME_ALLOTED = favoriteSettings[4]

print(FAVORITE_DATES)
