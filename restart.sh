#!/bin/bash

git pull 
PID=$(lsof -i:8081 | awk '{print $2}')
day=$(date | awk '{print $2$3$4}')
kill -9 $PID

nohup /root/anaconda3/envs/server/bin/python main.py 2 >&1 > ${day}.log & 
