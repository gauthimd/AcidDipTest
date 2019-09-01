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
      self.button = 17
      self.limit1 = 27
      self.limit2 = 22
      self.relaypins = [23,25,12,16]
      self.motorpins = [6,13,19,26]
      self.inputpins = [17,27,22]
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)
      for x in self.relaypins:
          GPIO.setup(x, GPIO.OUT)
          GPIO.output(x, GPIO.HIGH)
      for x in self.inputpins:
          GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.add_event_detect(27, GPIO.FALLING, callback=self.limit1callback, bouncetime=300)
      GPIO.add_event_detect(22, GPIO.FALLING, callback=self.limit2callback, bouncetime=300)
  
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
  
  def buttoncallback(self, channel):
      print("Button pressed")
  
  def limit1callback(self, channel):
      print("Limit1 reached")

  def limit2callback(self, channel):
      print("Limit2 reached")

  def run(self):
      time.sleep(2)
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
      self.displayReady()
      GPIO.wait_for_edge(17, GPIO.FALLING)
      print("17 grounded")
      lcd.lcd_clear()
      GPIO.cleanup()
      print("Done")

if __name__=="__main__":
    acid = AcidDipTester()
    acid.run()
