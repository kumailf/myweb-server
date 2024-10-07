#!/bin/bash

git pull 
PID=$(lsof -i:8081 | grep python | awk '{print $2}')
kill -9 $PID

day=$(date | awk '{print $2$3$4}')
nohup /root/anaconda3/envs/server/bin/python main.py 2 >&1 > ${day}.log &
