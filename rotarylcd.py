#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from datetime import datetime
import KY040, lcddriver, time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

lcd = lcddriver.lcd()
rot = KY040.KY040(21,20,24)

lcd.lcd_clear()
lcd.lcd_display_string("Hello",1)
lcd.lcd_display_string("Hello",2)
lcd.lcd_display_string("Hello",3)
lcd.lcd_display_string("Hello",4)
time.sleep(4)
lcd.lcd_clear()
