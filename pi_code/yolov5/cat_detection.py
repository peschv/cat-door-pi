# Date: Oct 11 2022
# Author: Vanessa Pesch
# Description: Handle instances of positive object detection by executing the following functions:
#     -notify() - send message and image to Telegram channel
#     -update_log() - update monthly log file
#     -find_cat() - identify if cat is 'IN' or 'OUT', take a screenshot, and call notify(),
#        update_log() and update_aggr_log() functions
#     -get_prev_detection() - get time of last detection, and return a calculated time interval between detections
#     -update_aggr_log() - update aggregate log by appending new running total of mins cat spent outside

import os
import torch
import time
from pathlib import Path
import subprocess
from datetime import datetime, timedelta
import telegram
import numpy as np
# Import variables from credentials.py
from credentials import TELEGRAM_BOT, TELEGRAM_CHAT

# The x-axis pixel that delineates the 'inside' from the 'outside' boundary line
boundary_pixel = 250

cat_name = "Sylvester" # Name of cat
object_label = "sylvester_face" # Object label

cwd = os.getcwd() # Current working directory

# Notify user on the Telegram channel by sending a text and screenshot. Uses the Python Telegram Bot.
# Parameters:
#        -location - the detected object's location, i.e. IN or OUT
#        -image - the screenshot taken of the detected object
#
# Modified from Python Telegram Bot API:
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API
def notify(location,image):
    bot = telegram.Bot(TELEGRAM_BOT) # Create new bot instance
    if location=='IN':
        bot.send_message(text=cat_name+' is waiting. Please let him OUT', chat_id = TELEGRAM_CHAT)
    elif location=='OUT':
        bot.send_message(text=cat_name+' is waiting. Please let him IN', chat_id = TELEGRAM_CHAT)
    bot.send_photo(photo=open(image, 'rb'), chat_id = TELEGRAM_CHAT)

# Update the log file with the timestamp, cat's label, and its location. Entries should be in the 
# form of YYYYMMDD-HHMMSS-label-location, such as 20220729-172611-sylvester_face-IN
# Parameters:
#        -timestamp - date and time of the detection
#        -obj_label - detected object's label name, ex. sylvester_face
#        -location - the detected object's location, i.e. either IN or OUT
def update_log(timestamp,obj_label,location):
    # Construct filename of log by using year and month, in the format of YYYYMM_log.txt
    filename = time.strftime('%Y%m')+'_log.txt'
   
    log_directory = cwd+'/data/logs/'  # Get log directory
    
    if not os.path.exists(log_directory): # Create directory if it does not exist
        os.makedirs(log_directory)
    os.chdir(log_directory)
    
    # Create the file if it does not exist, and on a new line, append timestamp, cat label and cat location
    f = open(filename, 'a+') 
    content = timestamp+'-'+obj_label+'-'+location+'\n'
    f.write(content)
    f.close()

# Find the cat's location to determine if the cat is outside or inside based on where the x_center and/or
# y_center point falls in relation to the boundary_pixel. Parameters:
#       -x_center - integer representing the midpoint between the x-min and x-max values of the detected object
#       -y_center - integer representing the midpoint between the y-min and y-max values of the detected object
# Take a screenshot, call notify() and update_log()
def find_cat(x_center, y_center):   

    # Get date and time of the detection
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    # Get the location and time interval of the previous detection from the log file
    log = get_prev_detection(timestamp)
    log_location = log[0] # Either OUT or IN
    log_interval = log[1] # Number of minutes between now and previous detection
    
    # Determine whether the cat is IN or OUT by the x-axis boundary_pixel 
    if x_center < boundary_pixel: 
        location = 'IN'
    else:
        location = 'OUT'
    print('location: ',location) # Print cat's location to console
        
    # If the correct object is detected, and the object is either in a different location or
    # >10min has passed indicating this is a new instance, then take screenshot, notify user and update logs.
    if (log_location != location or log_interval >= 10):       
        filename = str(timestamp) + '.jpg' # Create filename
        subprocess.run('/usr/bin/scrot -u '+cwd+'/data/images/'+filename,shell=True) # Take screenshot
        notify(location,cwd+'/data/images/'+filename) # Notify user
        
        # Log the opposite location, i.e. if cat is detected inside waiting to go outside,
        # log that the cat has moved outside, under the assumption that upon detection, the cat was
        # let in or out. Reason being that the framerate is too low to capture the cat's movemnet across
        # the in/out threshold of the door so to keep logs accurate, must record the sighting as
        # though the cat was immediately moved in or out.
        if location == 'IN':
            update_log(timestamp,object_label,'OUT') # Update log
            # Aggregate log is only updated when cat has moved inside, as its purpose is to log
            # the total time spent outside (which cannot be calculated if the cat just moved outside).
            update_aggr_log(timestamp,log_interval)
        else:
            update_log(timestamp,object_label,'IN') # Update log
            

# Retrieve last line in log file, calculate the time interval between current time and the timestamp
# of the last line. Return location and the calculated time interval in minutes. Parameters:
#      -curr_timestamp - current timestamp 
def get_prev_detection(curr_timestamp):
    
    file_date = (curr_timestamp[0:6]) # Get year and month
    file_path = cwd+'/data/logs/'+file_date+'_log.txt' # Get log directory
    
    if os.path.exists(file_path): # If the file exists
        last_line = Path(file_path).read_text().splitlines()[-1] # Get last line
        s = last_line.split("-") # Split the line to separate timestamp and location
        # Hold the line's timestamp and store in the format of YYYYMMDD-HHMMSS
        log_timestamp = s[0]+'-'+s[1] 
        log_location = s[3] # Hold the line's location; should be either IN or OUT
        
        # Calculate the time interval between log timestamp and current timestamp
        # Source code: https://www.programiz.com/python-programming/datetime/strptime
        log_timestamp = datetime.strptime(log_timestamp, "%Y%m%d-%H%M%S")
        curr_timestamp = datetime.strptime(curr_timestamp,"%Y%m%d-%H%M%S")
        interval = (curr_timestamp - log_timestamp)
        # Get total seconds of the time interval and convert to minutes
        interval_mins = round(interval.total_seconds()/60) 
        
    else: # If file doesn't exist, assume last location was cat going inside the previous evening
        log_location = 'IN'
        interval_mins = 0
        
    return log_location, interval_mins

# Update the aggregate_data.txt log that contains the running total of minutes the cat has spent outside per day
# Parameters:
#   -timestamp - current time and should be in the form of YYYYMMDD-HHMMSS
#   -prev_time - number of minutes that have passed since previous detection
def update_aggr_log(timestamp,prev_time):

    # Get current date, which is the first 8 characters of timestamp
    date = timestamp[0:8]     
    # Create the file if it does not exist, and append content
    f = open(cwd+'/data/logs/aggregate_data.txt','a+')
    
    # Try to open the aggregate log file, and write the new time intervals to it.
    # File extraction source code: https://stackoverflow.com/a/55595682
    try:
        file = Path(cwd+'/data/logs/aggregate_data.txt').read_text().splitlines()[-1]         
        aggr_prev_date = file.split(',')[0] # Get the date from the log line
        aggr_prev_interval = file.split(',')[-1] # Get the time interval from the log line
        
        if aggr_prev_date == date: # If line has same date as current date
            time_interval = int(aggr_prev_interval)+int(prev_time) # Add the two numbers together
            f.write(','+str(time_interval)) # Append the new time interval to the line
        else: # Add new entry  
            date_time_interval = date+','+str(prev_time)
            f.write('\n'+date_time_interval) # Write date and time interval on new line
            
    except IndexError: # Exception that occurs when file is empty
        # Add new entry
        time_interval = date+','+str(prev_time)
        f.write('\n'+time_interval)
    f.close()
    
