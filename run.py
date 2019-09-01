#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import time, lcddriver, RpiMotorLib, KY040
import RPi.GPIO as GPIO
from datetime import datetime

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
      self.limit1pin = 27
      self.limit2pin = 22
      self.relaypins = [23,25,12,16]
      self.motorpins = [6,13,19,26]
      self.inputpins = [17,27,22]
      self.limit1 = 0
      self.limit2 = 0
      self.rotary = KY040.KY040(21,20,24,self.rotaryCallback,self.switchCallback)
      GPIO.setwarnings(False)
      GPIO.setmode(GPIO.BCM)
      for x in self.relaypins:
          GPIO.setup(x, GPIO.OUT)
          GPIO.output(x, GPIO.HIGH)
      for x in self.inputpins:
          GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.add_event_detect(27, GPIO.FALLING, callback=self.limit1callback, bouncetime=300)
      GPIO.add_event_detect(22, GPIO.FALLING, callback=self.limit2callback, bouncetime=300)
      self.rotary.start()
  
  def rotaryCallback(self, direction):
      if direction == 0: rot = "clockwise"
      else: rot = "counterclockwise"
      print("Rotary turned", rot) 
  
  def switchCallback(self):
      print("Switch pressed") 

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
      self.limit1 = 1

  def limit2callback(self, channel):
      print("Limit2 reached")

  def limitTest(self):
      while True:
          print("Waiting for limit")
          time.sleep(.33)
          if self.limit1 == 1:
              self.limit1 = 0
              break
          else: continue

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
      self.limitTest()
      self.rotary.stop()
      GPIO.cleanup()
      print("Done")

if __name__=="__main__":
    acid = AcidDipTester()
    acid.run()
