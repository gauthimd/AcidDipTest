#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import time, datetime
import RPi.GPIO as GPIO

class Stepper():

    def __init__(self):
        self.pinlist = [6,13,19]
        self.enpin = 6
        self.dirpin = 13
        self.steppin = 19
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        for x in self.pinlist:
            GPIO.setup(x,GPIO.OUT)
        for x in self.pinlist:
            GPIO.output(x,GPIO.LOW)

    def step(self, revs, rotation=0, speed=1):
        x = 0
        steps = revs*3200
        GPIO.output(self.enpin, GPIO.HIGH)
        if rotation == 0:
            GPIO.output(self.dirpin, GPIO.LOW)
        else: GPIO.output(self.dirpin, GPIO.HIGH)
        start = datetime.datetime.now()
        while x < steps:
            x += 1
            GPIO.output(self.steppin, GPIO.HIGH)
            time.sleep(.000001/speed)
            GPIO.output(self.steppin, GPIO.LOW)
            time.sleep(.000001/speed)
        end = datetime.datetime.now()
        startmin = start.minute
        startsec = start.second
        endmin = end.minute
        endsec = end.second
        minutes = end.minute - start.minute
        print(startmin,startsec,endmin,endsec)
        seconds = minutes*60 + (endsec - startsec)
        print(revs)
        print(seconds)
        print(revs*60/seconds)
        GPIO.output(self.enpin, GPIO.LOW)

if __name__=="__main__":
    step = Stepper()
    step.step(90,1,1)
    GPIO.cleanup()
#143 steps station to station
