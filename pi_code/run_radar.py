# Optional Radar Component
# Description: Use the RCWL-0516 radar module to detect movement, and call detect.py from YOLOv5 
#   to run object detection when movement occurs.
# Date: Oct 11 2022
# Author: Vanessa Pesch
#
# Modified from source code:
# Author: Les Pounder
# Date: Oct 31 2017
# URL: https://www.electromaker.io/tutorial/blog/using-a-doppler-radar-sensor-with-the-raspberry-pi-12

from gpiozero import DigitalInputDevice
from time import sleep
import os
import subprocess

# Get current working directory
cwd = os.getcwd()

# Radar module using GPIO 17 pin. Pull-up set to false to set pin 'low' by default. Bounce
# time is the number of seconds that the radar will ignore changes in state after initial change.
radar = DigitalInputDevice(17, pull_up=False, bounce_time=30.0)

# Tries to call detect.py() to run the object detection by webcam. Prints error messages to
# console if exception occurs.
def detector():
    try:
        subprocess.run('libcamerify python3 '+cwd+'/yolov5/detect.py --weights '+cwd+
                       '/yolov5/best.pt --source 0 --conf-thres 0.8',shell=True, check=True)
    except subprocess.CalledProcessError as c:
        print('---------------Detect code was stopped--------------')
        print('Exit code: ', c.returncode)
       
# Call detector() function if radar is activated. Sleep for 2 seconds to free up CPU resources.
while True:
    radar.when_activated = detector
    sleep(2)