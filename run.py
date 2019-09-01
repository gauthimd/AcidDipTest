#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import time, lcddriver
import RPi.GPIO as GPIO
from datetime import datetime

class AcidDipTester():
  
  def __init__(self):
    lcd = lcddriver.lcd()
    lcd.lcd_clear()
    time.sleep(1)
    lcd.lcd_display_string("      PENA QC",1)
    lcd.lcd_display_string("    Booting....",3)
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

if __name__ = "
