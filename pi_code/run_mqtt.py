# Description: Uses Paho MQTT client to connect to an MQTT public broker and subscribe to topic to
#  receive messages from ESP32-S2 device. When message is received, send message to user via Telegram,
#  and update the monthly log file.
# Date: Oct 11 2022
# Author: Vanessa Pesch
#
# Modified from source code (with the exception of the notify() and update_log() functions):
# Author: Saiteng You
# Date: Aug 12 2020
# URL: https://www.emqx.com/en/blog/use-mqtt-with-raspberry-pi

import paho.mqtt.client as mqtt
import time
import telegram
import os
from pathlib import Path
# Import get_prev_detection() and update_aggr_log() methods from cat_detection.py
from yolov5.cat_detection import get_prev_detection, update_aggr_log
# Import variables TELEGRAM_BOT and TELEGRAM_CHAT from credentials.py
from yolov5.credentials import TELEGRAM_BOT, TELEGRAM_CHAT

cwd = os.getcwd() # Current working directory

cat_name = "Sylvester" # Name of cat
object_label = "sylvester_face" # Object label name
topic_name = "esp32/catmessage" # Name of subscription topic


# Callback function when trying to connect to broker. Subscribes to the desired topic
# when connection is successful. Parameters:
#      -client - the client instance
#      -userdata - users' information, typically empty
#      -flags - per Paho documentation, this is a dict that contains response flags from broker
#      -rc - the response code, where a value of 0 indicates successful connection
def on_connect(client, userdata, flags, rc):
    
    if rc == 0:  # If connection is successful
        print("We're connected") # Print success statement to console
        # Subscribe to topic esp32/catmessage with qos 0, meaning no acknowledgement required
        client.subscribe(topic_name,0) 

# Callback function when message received from broker. Parameters:
#     -client - the client instance
#     -userdata - users' information, typically empty
#     -msg - the message received from the broker
def on_message(client, userdata, msg):
    
    timestamp = time.strftime("%Y%m%d-%H%M%S") # Current timestamp    
    print("Time now: " + timestamp) # Print timestamp to console
    
    location = str(msg.payload).strip('b\'\"') # Get the location contained in the msg variable
    print("Message received: "+ location)  # Print the location to console
    
    # Check if the location is one of the two legitimate options of IN or OUT
    if location == "IN" or location == "OUT":
        # Call notify() to send the location to the user via the Telegram channel
        notify(location)
        # Call update_log() to update the log file
        update_log(timestamp,object_label,location)
        
        # Call get_prev_detection() to obtain the most recent location in the logs,
        # and return as an array of location and log interval in mins, where the interval
        # is the time between the most recent log and the current timestamp.
        log = get_prev_detection(timestamp) 
        log_location = log[0] # Location from the log
        log_interval = log[1] # Time interval from logged time to current time
        print('log: '+str(log))
        
        # If interval is greater than 30 minutes or previous log location is different
        # from current location, and the current location is "IN", then call update_aggr_log()
        # to update the aggregate_data.txt log file.
        if (log_location != location or log_interval >= 30) and location == "IN":
            update_aggr_log(timestamp,log_interval)

# Use the Python Telegram Bot to send message to user on specified Telegram channel.
# Parameters:
#      -location - the cat's location, either IN or OUT
#
# Adapted from Python Telegram Bot API:
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API
def notify(location):
    bot = telegram.Bot(TELEGRAM_BOT)
    if location == 'IN':
        bot.send_message(text=cat_name+' is inside', chat_id = TELEGRAM_CHAT)
    elif location == 'OUT':
        bot.send_message(text=cat_name+' is outside', chat_id = TELEGRAM_CHAT)
    
# Update the log file with entries in the form of YYYYMMDD-HHMMSS-label-location
# For example: 20220729-172611-sylvester_face-IN
# Parameters:
#       -timestamp - the timestamp when the message was received
#       -obj_label - the object's label name, ex. sylvester_face
#       -location - the cat's location, either IN or OUT
def update_log(timestamp,obj_label,location):
    # Log filename should be format of, ex., 202207_log.txt
    filename = time.strftime('%Y%m')+'_log.txt'
    # Get log directory
    log_directory = cwd+'/data/logs/'
    # Create the directory if it does not exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    os.chdir(log_directory)
    
    # Create the file if it does not exist, and append content
    f = open(filename, 'a+') 
    content = timestamp+'-'+obj_label+'-'+location+'\n'
    f.write(content)
    f.close()

# Create new MQTT client instance
client = mqtt.Client(client_id="paho-pi")
client.on_connect = on_connect
client.on_message = on_message

# Connect to EMQX broker, listening on port 1883 with keepalive set to 60 seconds
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()