#!/usr/bin/python3
# -*- coding: utf-8 -*-

import lcddriver, time
from datetime import datetime

lcd = lcddriver.lcd()
lcd.lcd_clear()
time.sleep(2)

lcd.lcd_clear()

try:
 while True:
     dateString = datetime.now().strftime('%b %d %y')
     timeString = datetime.now().strftime('%H:%M:%S')
     lcd.lcd_display_string("        Clock", 1)
     lcd.lcd_display_string(dateString+"   "+timeString, 3)
except KeyboardInterrupt:
 print("\nTurning off")
 time.sleep(.1)
 lcd.lcd_clear()
