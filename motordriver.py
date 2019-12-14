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
        while x < steps:
            x += 1
            GPIO.output(self.steppin, GPIO.HIGH)
            time.sleep(.000001/speed)
            GPIO.output(self.steppin, GPIO.LOW)
            time.sleep(.000001/speed)
        GPIO.output(self.enpin, GPIO.LOW)

if __name__=="__main__":
    step = Stepper()
    step.step(2,1,1)
    GPIO.cleanup()
#140 steps 0 dir Station 1 to Station 2
#140 steps 1 dir Station 2 to Station 1
#271 steps 1 dir Station 3 to Station 1
#131 steps 1 dir Station 3 to Station 2
#268 steps 0 dir Station 1 to Station 3 then homing()
#128 steps 0 dir Station 2 to Station 3 then homing()
