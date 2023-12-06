#!/bin/bash

day=$(date | awk '{print $2$3$4}')
nohup /root/anaconda3/envs/server/bin/python main.py 2 >&1 > ${day}.log &
