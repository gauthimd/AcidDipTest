#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import time, lcddriver
import RPi.GPIO as GPIO
from datetime import datetime

class AcidDipTester():
  
  def __init__(self):
    self.linactpin = 23
    self.sonicpin = 25
    self.pwrsplypin = 12
    self.sparepin = 16
    self.pins = [23,25,12,16]
    lcd = lcddriver.lcd()
    lcd.lcd_clear()
    time.sleep(1)
    lcd.lcd_display_string("      PENA QC",1)
    lcd.lcd_display_string("    Booting....",3)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for x in self.pins:
      GPIO.setup(x, GPIO.OUT)
      GPIO.output(x, GPIO.HIGH)
  
  def linactOn(self):
      GPIO.output(self.linactpin, GPIO.LOW)

  def linactOff(self):
      GPIO.output(self.linactpin, GPIO.HIGH)

  def sonicOn(self):
      GPIO.output(self.sonicpin, GPIO.LOW)

  def sonicOff(self):
      GPIO.output(self.sonicpin, GPIO.HIGH)

  def pwrsplyOn(self):
      GPIO.output(self.pwrsplypin, GPIO.LOW)
      
  def pwrsplyOff(self):
      GPIO.output(self.pwrsplypin, GPIO.HIGH)

if __name__=="__main__":
    acid = AcidDipTester()
    acid.linactOn()
    time.sleep(1)

