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
      self.switch = 0   #Switch and button variables, 1 or 0, used by callbacks
      self.button = 0
      self.limit = 0
      self.door = 0
      self.menuon = 0
      self.menuline = 1
      self.blinkline = 1
      self.rotaryswitch = KY040.KY040(21,20,24,self.rotaryCallback,self.switchCallback) 
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
      self.rotaryswitch.start()
  
  #Callback functions are called when input is received.
  def rotaryCallback(self, rot):
      if self.menuon == 1:
          if rot == 0:
              self.menuline +=1
              if self.menuline > 7: self.menuline = 1
          else:
              self.menuline -=1
              if self.menuline < 1: self.menuline = 7
      print(self.menuline)

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

  def displayDoor(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("     Door Ajar",2)
      lcd.lcd_display_string("Close Door to Resume",4)
      
      
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
  def homing(self):
      self.displayHoming()
      self.limit = 0  
      while True:
          time.sleep(.33)
          if self.limit == 1:
              self.limit = 0
              break
          else: continue
  
  def ready(self):
      self.displayReady()
      t1 = self.blinkOn()
      while True:
          if self.button == 1:
              self.button = 0
              self.blinkOff(t1)
              self.lightOn()
              x = 1
              break
          elif self.switch == 1:
              self.switch = 0
              self.blinkOff(t1)
              x = 2
              break
          elif self.door == 1:
              self.blinkOff(t1)
              x = 3
              break
          time.sleep(.33)
      if x == 1: 
          return self.run()
      elif x == 2: 
          return self.menu()
      elif x == 3: 
          return self.doorAjar()

  def doorAjar(self):
      self.displayDoor()
      #while door is still open, do nothing

  def boot(self):
      self.displayBooting()
      time.sleep(2)
      self.homing()
      self.ready()
  
  def menu(self):
      print("menu")
      self.menuon = 1
      menu = {1:"Set Sonication Time",2:"Extend actuator",3:"Turn On Power Supply",
              4:"Turn On Sonicator",5:"Move to Station 1",6:"Move to Station 2",
              7:"Exit"}
      z = 0 
      while self.switch == 0:
          if self.menuline <= 4:
              for x in range(1,5):
                  if x == self.menuline:
                      if z == 1:
                          lcd.lcd_display_string(menu[x],x)
                          z = 0
                      elif z == 0:
                          lcd.lcd_display_string("",x)
                          z = 1
                  else: 
                      lcd.lcd_display_string(menu[x],x)
              time.sleep(.5)
              lcd.lcd_clear()
          else:
              for x in range(5,8):
                  if x == self.menuline:
                      if z == 1:
                          lcd.lcd_display_string(menu[x],x-4)
                          lcd.lcd_display_string("",4)
                          z = 0
                      elif z == 0:
                          lcd.lcd_display_string("",x-4)
                          lcd.lcd_display_string("",4)
                          z = 1
                  else: 
                      lcd.lcd_display_string(menu[x],x-4)
                      lcd.lcd_display_string("",4)
              time.sleep(.5)
              lcd.lcd_clear()
      if self.menuline == 7: 
          self.switch = 0
          self.menuon = 0
          self.ready()
      self.menuon = 0

if __name__== "__main__":
    acid = AcidDipTester()
    acid.boot()
    print("Done")
