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
      self.linactpin = 18        #Relay pins
      self.sonicpin = 25
      self.pwrsplypin = 12
      self.lightpin = 16
      self.buttonpin = 17        #Button and switch inputs
      self.limitpin = 27
      self.doorpin1 = 22
      self.doorpin2 = 4
      self.relaypins = [18,25,12,16]  #Relay pin list
      self.motorpins = [6,13,19,26]   #Motor pin list
      self.inputpins = [17,27,22,4]     #Input pin list
      self.switch = 0   #Switch and button variables, 1 or 0, used by callbacks
      self.button = 0
      self.limit = 0
      self.door = 0
      self.mainmenu = 0 # These bits keep track of which menu and line are selected
      self.sonicmenu = 0
      self.sonictime = 30
      self.menuline = 1
      self.position = None
      self.auto = 0
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
      GPIO.add_event_detect(4, GPIO.FALLING, callback=self.doorcallback, bouncetime=300)
      self.rotaryswitch.start()
  
  #Callback functions are called when input is received.
  def rotaryCallback(self, rot):
      if self.mainmenu == 1:
          if rot == 0:
              self.menuline +=1
              if self.menuline > 7: self.menuline = 1
          else:
              self.menuline -=1
              if self.menuline < 1: self.menuline = 7
      if self.sonicmenu == 1:
          if rot == 0:
              self.sonictime +=1
              if self.sonictime >= 30: self.sonictime = 30
          else:
              self.sonictime -=1
              if self.sonictime <= 0: self.sonictime = 0
      print(self.menuline, self.sonictime)

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

  #Define easy to use functions for turning the relays on/off
  def lightOn(self):
      GPIO.output(self.lightpin, GPIO.LOW)

  def lightOff(self):
      GPIO.output(self.lightpin, GPIO.HIGH)

  def linactOn(self):
      print("linactOn")
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
      lcd.lcd_clear()
      time.sleep(.1)
      self.limit = 0  
      while GPIO.input(self.limitpin) == True:
          lcd.lcd_display_string("       Homing",1)
          lcd.lcd_display_string("   Please wait...",3)
          time.sleep(.33)
          if self.door == 1: self.doorAjar()
      self.position = 3
  
  def ready(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("        Ready",1)
      lcd.lcd_display_string("    Press Button",3)
      lcd.lcd_display_string("      to Begin",4)
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
          self.autoRun()
      elif x == 2: 
          self.menu()
      elif x == 3: 
          self.doorAjar()
          self.ready()

  def doorAjar(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("     Door Ajar",2)
      lcd.lcd_display_string("Close Door to Resume",4)
      while GPIO.input(self.doorpin1) == False or GPIO.input(self.doorpin2) == False:
          time.sleep(.5)
      self.door = 0
      lcd.lcd_clear()

  def boot(self):
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("      PENA QC",1)
      lcd.lcd_display_string("   Acid Dip Test",2)
      lcd.lcd_display_string("    Booting....",3)
      time.sleep(2)
      self.homing()
      self.ready()
  
  def menu(self):
      print("menu")
      lcd.lcd_clear()
      self.mainmenu = 1
      if self.position == 1:
          menu = {1:"Set Sonication Time",2:" Move to Station 2",3:"Return to Home Pos.",4:"  Extend Actuator",
                  5:"Turn On Power Supply",6:" Turn On Sonicator",7:"        Exit"}
      if self.position == 2:
          menu = {1:"Set Sonication Time",2:" Move to Station 1",3:"Return to Home Pos.",4:"  Extend Actuator",
                  5:"Turn On Power Supply",6:" Turn On Sonicator",7:"        Exit"}
      if self.position == 3:
          menu = {1:"Set Sonication Time",2:" Move to Station 1",3:" Move to Station 2",4:"  Extend Actuator",
                  5:"Turn On Power Supply",6:" Turn On Sonicator",7:"        Exit"}
          z = 0
          while self.switch == 0:
              if z == 0:
                  lcd.lcd_display_string("        Menu",1)
                  lcd.lcd_display_string(menu[self.menuline],2)
                  lcd.lcd_display_string("Press knob to select",4)
                  time.sleep(.33)
                  z = 1
              else:
                  lcd.lcd_display_string("                    ",2)
                  time.sleep(.33)
                  z = 0
              if self.door == 1: self.doorAjar()
          if self.menuline == 1: 
              self.switch = 0
              self.mainmenu = 0
              self.setSonictime()
          elif self.menuline == 2: 
              self.switch = 0
              self.mainmenu = 0
              self.movetoStation()
          elif self.menuline == 3: 
              self.switch = 0
              self.mainmenu = 0
              if self.position == 3: self.movetoStation()
              else: self.homing()
          elif self.menuline == 4 or self.menuline == 5 or self.menuline == 6: 
              self.switch = 0
              self.mainmenu = 0
              self.manualEnable()
          elif self.menuline == 7: 
              self.switch = 0
              self.mainmenu = 0
              self.ready()
          self.mainmenu = 0

  def setSonictime(self):
      self.sonicmenu = 1
      lcd.lcd_clear()
      while self.switch == 0:
          lcd.lcd_display_string("Set Sonication Time:",1)
          lcd.lcd_display_string("         "+str(self.sonictime).zfill(2),2)
          lcd.lcd_display_string("  Use Knob to Set",3)
          lcd.lcd_display_string(" Press Knob to Save",4)
          time.sleep(.5)
          if self.door == 1: self.doorAjar()
      lcd.lcd_clear()
      lcd.lcd_display_string("  Sonication Time",1)
      lcd.lcd_display_string("         "+str(self.sonictime),2)
      lcd.lcd_display_string("       Saved",3)
      lcd.lcd_display_string("                    ",4)
      time.sleep(2)
      self.switch = 0
      self.sonicmenu =0
      self.menu()

  def movetoStation(self,num):
      x = 1
      if self.pos = 1:
          if self.menuline = 2: x = 2
      if self.pos = 2:
          if self.menuline =2: x = 1
      if self.pos = 3:
          if self.menuline =2: x = 1
          else: x = 2   
      x = str(x)
      self.lightOn()
      print("Moving to Station "+x)
      lcd.lcd_clear()
      lcd.lcd_display_string("Moving to Station "+x,2) 
      lcd.lcd_display_string("   Please Wait...",3) 
      x = 0
      while x < 5:
          lcd.lcd_display_string("Moving to Station "+x,2) 
          lcd.lcd_display_string("   Please Wait...",3) 
          time.sleep(.5)
          x += 0.5
          if self.door == 1: 
              self.lightOff()
              self.doorAjar()
              self.lightOn()
      self.position = int(x)
      self.lightOff()
      self.menu()

  def manualEnable(self):
      x = 0
      if self.menuline == 4: self.linactOn()
      elif self.menuline == 5: self.pwrsplyOn()
      elif self.menuline == 6: self.sonicOn()
      self.lightOn()
      lcd.lcd_clear()
      while self.switch == 0:
          if self.menuline == 4:  lcd.lcd_display_string(" Actuator Extended",1)
          elif self.menuline ==5: lcd.lcd_display_string("  Power Supply On",1) 
          elif self.menuline ==6: lcd.lcd_display_string("    Sonicator On",1) 
          lcd.lcd_display_string("     Press Knob",3) 
          if self.menuline == 4:  lcd.lcd_display_string("     to Retract",4) 
          else:                   lcd.lcd_display_string("    to Turn Off",4) 
          if self.door == 1:
              x = 1
              break
          time.sleep(.5)
      if self.menuline == 4: self.linactOff()
      elif self.menuline == 5: self.pwrsplyOff()
      elif self.menuline == 6: self.sonicOff()
      self.lightOff()
      if x == 1:
          lcd.lcd_clear()
          lcd.lcd_display_string("    Door Opened",2) 
          if self.menuline ==4 :  lcd.lcd_display_string("   Retracting...",3) 
          else:                   lcd.lcd_display_string("   Turning Off...",3) 
          time.sleep(2)
      self.switch = 0
      self.menu()

  def autoRun(self):
      self.auto = 1
      print("Running")
      time.sleep(5)
      print("Complete!")
      time.sleep(2)
      self.ready()

if __name__== "__main__":
    acid = AcidDipTester()
    acid.boot()
    print("Done")
