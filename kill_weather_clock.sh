#!/bin/bash

# get pid of weather clock process
weather_clock_pid=$("./get_weather_clock_pid.sh")

# check to make sure it got a PID
if [ -z "$weather_clock_pid" ]; then
    echo "The PID for weather_clock.py could not be found"
    exit 1
fi

# kill the process
echo "Killing weather_clock.py..."
sudo kill --signal SIGINT $weather_clock_pid
echo "  --> Killed."
