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
    next_midnight = pst_now.replace(hour=1, minute=38, second=0, microsecond=0) + timedelta(days=0)
    # ^to test make days=0 and change time accordingly
    
    time_difference = next_midnight - pst_now
    
    # Convert the time difference to seconds
    seconds_to_wait = time_difference.total_seconds()
    return seconds_to_wait
