#!/bin/bash

# Description: Listen for MQTT messages and run the radar component inside
#   the virtual environment.
# Date: Oct 10 2022
# Author: Vanessa Pesch

# Activate virtual environment.
# In this case, the name of the virtual environment is myyolo
source myyolo/bin/activate

# Navigate to virtual environment directory.
cd myyolo

# Start run_mqtt and run_radar as background processes.
python3 /home/pi/myyolo/run_radar.py &
python3 /home/pi/myyolo/run_mqtt.py &