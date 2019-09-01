#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import time, lcddriver
import RPi.GPIO as GPIO
from datetime import datetime
import RpiMotorLib

lcd = lcddriver.lcd()
stepper = RpiMotorLib.BYJMotor("Stepper", "Nema")

class AcidDipTester():
  
  def __init__(self):
      self.displayBooting()
      self.linactpin = 23
      self.sonicpin = 25
      self.pwrsplypin = 12
      self.sparepin = 16
      self.relaypins = [23,25,12,16]
      self.motorpins = [6,13,19,26]
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)
      for x in self.relaypins:
        GPIO.setup(x, GPIO.OUT)
        GPIO.output(x, GPIO.HIGH)
  
  def displayReady(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("        Ready",1)
      lcd.lcd_display_string("    Press Button",3)
      lcd.lcd_display_string("      to Begin",4)

  def displayBooting(self):
      lcd.lcd_clear()
      time.sleep(1)
      lcd.lcd_display_string("      PENA QC",1)
      lcd.lcd_display_string("   Acid Dip Test",2)
      lcd.lcd_display_string("    Booting....",3)

  def displayHoming(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("       Homing",1)
      lcd.lcd_display_string("   Please wait...",3)

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

  def run(self):
      time.sleep(1)
      self.displayReady()
      self.linactOn()
      time.sleep(1)
      self.linactOff()
      time.sleep(.25)
      self.sonicOn()
      time.sleep(1)
      self.sonicOff()
      self.displayHoming()
      time.sleep(.25)
      self.pwrsplyOn()
      time.sleep(1)
      self.pwrsplyOff()
      lcd.lcd_clear()
      GPIO.cleanup()

if __name__=="__main__":
    acid = AcidDipTester()
    acid.run()
