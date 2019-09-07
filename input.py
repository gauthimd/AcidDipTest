#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from datetime import datetime
import KY040, lcddriver, time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)

while GPIO.input(17) == True:
    print("waiting...is the hardest part")
    time.sleep(.2)

print("Exit")
