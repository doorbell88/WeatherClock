#!/bin/bash

# name of weather clock python program
weather_clock_py="$1"

# get pid of weather clock process
weather_clock_pid=$(ps -ef | grep "$weather_clock_py" | grep "root" | awk '{print $2}')

# kill the process
sudo kill --signal SIGINT $weather_clock_pid
