#!/usr/bin/python3
# -*- encoding: utf-8 -*-

#Import all necessary objects. The lcddriver is for the lcd display
#The RpiMotorLib is for the stepper motor, and the KY040 is for the rotary encoder
import time, lcddriver, RpiMotorLib, KY040, threading
import RPi.GPIO as GPIO
from datetime import datetime

#Create objects for lcd and stepper motor
lcd = lcddriver.lcd()
stepper = RpiMotorLib.BYJMotor("Stepper", "Nema")


class AcidDipTester():
  
  def __init__(self):
      self.displayBooting()      #Boot screen
      self.linactpin = 23        #Relay pins
      self.sonicpin = 25
      self.pwrsplypin = 12
      self.lightpin = 16
      self.buttonpin = 17        #Button and switch inputs
      self.limitpin = 27
      self.doorpin = 22
      self.relaypins = [23,25,12,16]  #Relay pin list
      self.motorpins = [6,13,19,26]   #Motor pin list
      self.inputpins = [17,27,22]     #Input pin list
      self.rotswitch = 0   #Switch and button variables, 1 or 0, used by callbacks
      self.button = 0
      self.limit = 0
      self.door = 0
      #I needed the callbacks in the object, that's why instantiated in init
      self.rotary = KY040.KY040(21,20,24,self.rotaryCallback,self.switchCallback) 
      GPIO.setwarnings(False)   #GPIO setup
      GPIO.setmode(GPIO.BCM)
      for x in self.relaypins:    #Set all relays to HIGH. This turns off all relays
          GPIO.setup(x, GPIO.OUT)
          GPIO.output(x, GPIO.HIGH)
      for x in self.inputpins:  #Set pull up resistors on input pins. Switches pull pin low
          GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      #Set callbacks for limit switch detection
      GPIO.add_event_detect(27, GPIO.FALLING, callback=self.limitcallback, bouncetime=300)
      GPIO.add_event_detect(22, GPIO.FALLING, callback=self.doorcallback, bouncetime=300)
      self.rotary.start()
  
  #Callback functions are called when input is received.
  def rotaryCallback(self, direction):
      if direction == 0: rot = "clockwise"
      else: rot = "counterclockwise"
      print("Rotary turned", rot) 
  
  def switchCallback(self):
      self.switch = 1
      print("Switch pressed") 

  def buttoncallback(self, channel):
      self.button = 1
      print("Button pressed")
  
  def limitcallback(self, channel):
      print("Limit reached")
      self.limit = 1

  def doorcallback(self, channel):
      self.door = 1
      print("Door Ajar")

  #Display screens
  def displayReady(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("        Ready",1)
      lcd.lcd_display_string("    Press Button",3)
      lcd.lcd_display_string("      to Begin",4)

  def displayBooting(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("      PENA QC",1)
      lcd.lcd_display_string("   Acid Dip Test",2)
      lcd.lcd_display_string("    Booting....",3)

  def displayHoming(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("       Homing",1)
      lcd.lcd_display_string("   Please wait...",3)

  #Define easy to use functions for turning the relays on/off
  def lightOn(self):
      GPIO.output(self.lightpin, GPIO.LOW)

  def lightOff(self):
      GPIO.output(self.lightpin, GPIO.HIGH)

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

  def blinkOn(self):
      t1 = threading.Thread(target=self.blinking)
      t1.daemon = True
      t1.start()
      return t1
  
  def blinkOff(self, t1):
      t1.do_run = False
      t1.join()

  def blinking(self):
      th = threading.currentThread()
      while getattr(th, "do_run", True):
          self.lightOn()
          time.sleep(.33)
          self.lightOff()
          time.sleep(.33)
  
  #This will be my Homing function
  def HomingTest(self):
      self.displayHoming()
      self.limit = 0  
      while True:
          time.sleep(.33)
          if self.limit == 1:
              self.limit = 0
              break
          else: continue
  
  def readymode(self):
      self.displayReady()
      self.

  def run(self):
      self.displayBooting()
      time.sleep(3)
      t1 = self.blinkOn()
      self.displayHoming()
      time.sleep(10)
      self.sonicOn()
      time.sleep(2)
      self.sonicOff()
      self.pwrsplyOn()
      time.sleep(2)
      self.pwrsplyOff()
      self.blinkOff(t1)
      lcd.lcd_display_string("        Done",2)
      time.sleep(2)
      lcd.lcd_backlight("Off")
      GPIO.cleanup()

if __name__=="__main__":
    acid = AcidDipTester()
    acid.run()
