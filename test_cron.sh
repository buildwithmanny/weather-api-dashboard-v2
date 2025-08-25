#!/bin/bash
export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd "/Users/manuelvelazquez/Desktop/dataresumes/weather-api-dashboard-v2" || exit 1

# Run and capture output
"/Library/Frameworks/Python.framework/Versions/3.12/bin/python3" main.py > fetch.log 2>&1
code=$?

# Always leave breadcrumbs
date +"[%Y-%m-%d %H:%M:%S] 1min test tick (exit=$code)" >> heartbeat.log
pwd > last_run.pwd
