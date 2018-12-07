#!/bin/sh

ps -ef | grep *_maker.py | grep -v grep | grep -v UID | awk '{printf("kill -9 %s\n",$2)}' | sh
ps -ef | grep *_robot.py | grep -v grep | grep -v UID | awk '{printf("kill -9 %s\n",$2)}' | sh
ps -ef | grep *_hedge.py | grep -v grep | grep -v UID | awk '{printf("kill -9 %s\n",$2)}' | sh