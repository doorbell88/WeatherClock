#!/bin/bash

# get pid of weather clock process
weather_clock_pid=$(ps -ef | grep python | grep "weather_clock.py" | \
                    grep -v grep | grep "root" | grep -v sudo | \
                    awk '{print $2}' | head -n 1)

# echo PID to terminal
echo $weather_clock_pid
