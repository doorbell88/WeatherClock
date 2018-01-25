#!/bin/bash

set -e

# CONSTANTS
FILE="/etc/rc.local"

# get line number of "$pattern"
get_line_number() {
    pattern="$1"
    line_number=$(grep -n $FILE -e $pattern \
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
    sed -i "${line_number}i $content" $FILE
    # increment $line_number
    line_number=$((line_number + 1))
}

#===============================================================================
#                                     MAIN
#-------------------------------------------------------------------------------

# get line number where "exit 0" occurs
get_line_number "exit"

# insert lines into file
insert_line
insert_line "/home/pi/WeatherClock/shutdown_switch.py &"
insert_line "/home/pi/WeatherClock/weather_clock.py &"
insert_line
