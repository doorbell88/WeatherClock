#!/bin/bash

#-------------------------------------------------------------------------------
# Adds scripts to run at bootup.  Namely, adds the following to /etc/rc.local
#   - shutdown_switch.py (to listen for a button press, and send a shutdown
#                         command so the RaspberryPi shuts down safely)
#   - weather_clock.py   (to run the weather clock)
#-------------------------------------------------------------------------------

set -e

# CONSTANTS
FILE="/etc/rc.local"

# get line number of "$pattern"
get_line_number() {
    pattern="$1"
    line_number=$(grep -n ${FILE} -e ${pattern} \
                  | tail -n 1               \
                  | sed 's/:/ /'            \
                  | awk '{print $1}'        \
                 )
}

# function to insert a line at the current $line_number
insert_line() {
    if [ -n "$1" ]; then
        content="$1"
    else
        content="\ "
    fi

    # insert line
    sed -i "${line_number}i ${content}" ${FILE}
    # increment $line_number
    line_number=$((line_number + 1))
}

#===============================================================================
#                                     MAIN
#-------------------------------------------------------------------------------

# First, make a backup!
cp ${FILE}{,.bak}

# get line number where "exit 0" occurs
get_line_number "exit"

# insert lines into file
insert_line
insert_line "/home/pi/WeatherClock/shutdown_switch.py &"
insert_line "/home/pi/WeatherClock/weather_clock.py &"
insert_line
