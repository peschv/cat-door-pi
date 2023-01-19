#!/bin/bash

# Description: Shut down the run_mqtt and run_radar background processes.
# Date: Oct 10 2022
# Author: Vanessa Pesch
#
# Source code: 
# Author: Aurora0001
# Date: Jan 19 2018
# URL: https://raspberrypi.stackexchange.com/a/78015

pgrep -f run_mqtt | xargs kill
pgrep -f run_radar | xargs kill

# Return to home directory
cd

# Exit shell
exit