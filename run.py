#!/usr/bin/python3
# -*- encoding: utf-8 -*-

#Import all necessary objects. The lcddriver is for the lcd display
#The RpiMotorLib is for the stepper motor, and the KY040 is for the rotary encoder
import time, lcddriver, KY040, threading
import RPi.GPIO as GPIO
from datetime import datetime
from motordriver import Stepper
from serialps import powerSupply
from jsonhelper import JSON

#Create objects for lcd and stepper motor
lcd = lcddriver.lcd()
step = Stepper()
power = powerSupply(24,3)
jsn = JSON()

class AcidDipTester():
  
  def __init__(self):
      self.linactpin1 = 18        #Relay pins
      self.linactpin2 = 16
      self.sonicpin1 = 8
      self.sonicpin2 = 25
      self.pwrsplypin = 12
      self.fanpin = 7
      self.relayspare1 = 10
      self.relayspare2 = 9
      self.buttonpin = 17        #Button and switch inputs
      self.limitpin = 27
      self.doorpin1 = 22
      self.doorpin2 = 4
      self.relaypins = [18,25,12,16,8,7,10,9]  #Relay pin list
      self.motorpins = [6,13,19]   #Motor pin list
      self.inputpins = [17,27,22,4]     #Input pin list
      self.lightpin = 5       #PWM output used to drive button light
      self.switch = 0   #Switch and button variables, 1 or 0, used by callbacks
      self.button = 0
      self.limit = 0
      self.door = 0
      self.mainmenu = 0 # These bits keep track of which menu and line are selected
      self.sonicmenu = 0
      self.sonictime, self.position = jsn.readJSON()
      self.menuline = 1
      self.auto = 0
      self.rotaryswitch = KY040.KY040(21,20,24,self.rotaryCallback,self.switchCallback) 
      GPIO.setwarnings(False)   #GPIO setup
      GPIO.setmode(GPIO.BCM)
      for x in self.relaypins:    #Set all relays to HIGH. This turns off all relays
          GPIO.setup(x, GPIO.OUT)
          GPIO.output(x, GPIO.HIGH)
      for x in self.inputpins:  #Set pull up resistors on input pins. Switches pull pin low
          GPIO.setup(x, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.setup(5, GPIO.OUT)
      self.pwm = GPIO.PWM(5, 200) #Set pin 5 as pwm output to drive power MOSFET for 24V button light
      self.pwm.start(0)
      #Set callbacks for limit switch detection
      GPIO.add_event_detect(17, GPIO.FALLING, callback=self.buttoncallback, bouncetime=300)
      GPIO.add_event_detect(27, GPIO.FALLING, callback=self.limitcallback, bouncetime=300)
      GPIO.add_event_detect(22, GPIO.FALLING, callback=self.doorcallback, bouncetime=300)
      GPIO.add_event_detect(4, GPIO.FALLING, callback=self.doorcallback, bouncetime=300)
      self.rotaryswitch.start()
#      self.fanOn()
  
  #Callback functions are called when input is received.
  def rotaryCallback(self, rot):
      if self.mainmenu == 1:
          if rot == 0:
              self.menuline +=1
              if self.position == 3:
                  if self.menuline > 8: self.menuline = 1
              else:
                  if self.menuline > 7: self.menuline = 1
          else:
              self.menuline -=1
              if self.position == 3:
                  if self.menuline < 1: self.menuline = 8
              else:
                  if self.menuline < 1: self.menuline = 7
      if self.sonicmenu == 1:
          if rot == 0:
              self.sonictime +=1
              if self.sonictime >= 30: self.sonictime = 30
          else:
              self.sonictime -=1
              if self.sonictime <= 0: self.sonictime = 0
      print("Rotary rotated")

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
      self.pwm.ChangeDutyCycle(100)

  def lightOff(self):
      self.pwm.ChangeDutyCycle(0)

  def linactOn(self):
      GPIO.output(self.linactpin1, GPIO.LOW)
      GPIO.output(self.linactpin2, GPIO.LOW)
      time.sleep(1)
      self.reset()

  def linactOff(self):
      GPIO.output(self.linactpin1, GPIO.HIGH)
      GPIO.output(self.linactpin2, GPIO.HIGH)
      time.sleep(1)
      self.reset()

  def sonic1On(self):
      GPIO.output(self.sonicpin1, GPIO.LOW)
      time.sleep(.5)
      self.reset()

  def sonic1Off(self):
      GPIO.output(self.sonicpin1, GPIO.HIGH)
      time.sleep(.5)
      self.reset()

  def sonic2On(self):
      GPIO.output(self.sonicpin2, GPIO.LOW)
      time.sleep(.5)
      self.reset()

  def sonic2Off(self):
      GPIO.output(self.sonicpin2, GPIO.HIGH)
      time.sleep(.5)
      self.reset()

  def pwrsplyOn(self):
      GPIO.output(self.pwrsplypin, GPIO.LOW)
      time.sleep(3)
      power.connect()
      power.turnOn()
      time.sleep(.5)
      self.reset()
      
  def pwrsplyOff(self):
      power.turnOff()
      time.sleep(1)
      power.close()
      time.sleep(1)
      GPIO.output(self.pwrsplypin, GPIO.HIGH)
      time.sleep(.5)
      self.reset()

  def fanOn(self):
      GPIO.output(self.fanpin, GPIO.LOW)
      time.sleep(.5)
      self.reset()
      
  def fanOff(self):
      GPIO.output(self.fanpin, GPIO.HIGH)
      time.sleep(.5)
      self.reset()

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
          for x in range(0,101,10):
              self.pwm.ChangeDutyCycle(x)
              time.sleep(.05)
              if self.button == 1: 
                  break
              elif self.switch == 1: 
                  break
          for x in range(95,0,-10):
              self.pwm.ChangeDutyCycle(x)
              time.sleep(.05)
              if self.button == 1: 
                  break
              elif self.switch == 1: 
                  break

  def motorStart(self,revs,rotation):
      t2 = threading.Thread(target=self.motorRun, args=(revs,rotation,))
      t2.daemon = True
      t2.start()
      return t2

  def motorRun(self,revs,rotation): #need more than 1 step and a check, need all steps in thead and checks in another
      th = threading.currentThread()
      x = 0
      while getattr(th,"do_run",True) and x < revs:
          step.step(1,rotation)
          x+= 1
          if self.door == 1: 
              self.lightOff()
              self.doorAjar()
              self.lightOn()
          if self.limit == 1:
              step.step(5,1)
              self.limit = 0
              break
      th.do_run = False

  def motorStop(self,t2):
      t2.do_run = False
      t2.join()

  #This will be my Homing function
  def homing(self):
      self.lightOn()
      self.reset()
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("       Homing",1)
      lcd.lcd_display_string("   Please wait...",3)
      if self.position == 1: step.step(268,0)
      elif self.position == 2: step.step(128,0)
      while self.limit == 0:
          lcd.lcd_display_string("       Homing",1)
          lcd.lcd_display_string("   Please wait...",3)
          step.step(1,0)
          time.sleep(.1)
          if self.door == 1: 
              self.lightOff()
              self.doorAjar()
              self.lightOn()
      step.step(2,1)
      self.lightOff()
      self.limit = 0
      self.position = 3
      jsn.writeJSON(self.sonictime, self.position)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("       Homing",1)
      lcd.lcd_display_string("     Complete!",3)
      time.sleep(1)
  
  def ready(self):
      self.reset()
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
              self.lightOff()
              x = 2
              break
          elif self.door == 1:
              self.blinkOff(t1)
              self.lightOff()
              x = 3
              break
          time.sleep(.03)
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
      time.sleep(3)
      self.homing()
      self.ready()
  
  def menu(self):
      print("menu")
      lcd.lcd_clear()
      time.sleep(.1)
      self.reset()
      self.mainmenu = 1
      self.menudict = {}
      if self.position == 1:
          self.menudict = {1:"Set Sonication Time",2:" Move to Station 2",3:"Return to Home Pos.",4:"  Extend Actuator",
                  5:"Turn On Power Supply",6:" Turn On Sonicator 1",7:" Turn On Sonicator 2"}
      if self.position == 2:
          self.menudict = {1:"Set Sonication Time",2:" Move to Station 1",3:"Return to Home Pos.",4:"  Extend Actuator",
                           5:"Turn On Power Supply",6:" Turn On Sonicator 1",7:" Turn On Sonicator 2"}
      if self.position == 3:
          self.menudict = {1:"Set Sonication Time",2:" Move to Station 1",3:" Move to Station 2",4:"  Extend Actuator",
                           5:"Turn On Power Supply",6:" Turn On Sonicator 1",7:" Turn On Sonicator 2",8:"        Exit"}
      z = 0
      while self.switch == 0:
          if z == 0:
              lcd.lcd_display_string("        Menu",1)
              lcd.lcd_display_string(self.menudict[self.menuline],2)
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
          else: 
              self.homing()
              self.menu()
      elif self.menuline == 4 or self.menuline == 5 or self.menuline == 6 or self.menuline == 7: 
          self.switch = 0
          self.mainmenu = 0
          self.manualEnable()
      elif self.menuline == 8: 
          self.switch = 0
          self.mainmenu = 0
          self.ready()
      self.mainmenu = 0

  def setSonictime(self):
      self.sonicmenu = 1
      lcd.lcd_clear()
      time.sleep(.1)
      while self.switch == 0:
          lcd.lcd_display_string("Set Sonication Time:",1)
          lcd.lcd_display_string("         "+str(self.sonictime).zfill(2),2)
          lcd.lcd_display_string("  Use Knob to Set",3)
          lcd.lcd_display_string(" Press Knob to Save",4)
          time.sleep(.25)
          if self.door == 1: self.doorAjar()
      jsn.writeJSON(self.sonictime, self.position)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("  Sonication Time",1)
      lcd.lcd_display_string("         "+str(self.sonictime),2)
      lcd.lcd_display_string("       Saved",3)
      lcd.lcd_display_string("                    ",4)
      time.sleep(2)
      self.switch = 0
      self.sonicmenu = 0
      self.menu()

  def movetoStation(self): 
      x = 1
      z = 1
      if self.position == 1:
          if self.menuline == 2: 
              x = 2 #Station 1 to Station 2
              z = 1 #140steps 0 dir
      if self.position == 2:
          if self.menuline == 2: 
              x = 1 #Station 2 to Station 1
              z = 2 #140steps 1 dir
      if self.position == 3:
          if self.menuline == 2: 
              x = 1 #Station 3 to Station 1
              z = 3 #271steps 1 dir
          else: 
              x = 2 #Station 3 to Station 2
              z = 4 #131steps 1 dir
      x = str(x)
      self.lightOn()
      print("Moving to Station "+x)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("Moving to Station "+x,2) 
      lcd.lcd_display_string("   Please Wait...",3) 
      if z == 1: 
          self.position = int(x)
          jsn.writeJSON(self.sonictime, self.position)
          step.step(140,0) 
      if z == 2: 
          step.step(140,1)
          self.position = int(x)
          jsn.writeJSON(self.sonictime, self.position)
      if z == 3: 
          step.step(271,1)
          self.position = int(x)
          jsn.writeJSON(self.sonictime, self.position)
      if z == 4: 
          step.step(131,1)
          self.position = int(x)
          jsn.writeJSON(self.sonictime, self.position)
      print("Position " + str(self.position))
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("      Complete!",3)
      time.sleep(2)
      lcd.lcd_clear()
      self.lightOff()
      self.menu()

  def reset(self):
      self.door = 0
      self.limit = 0
      self.button = 0
      self.switch = 0
      print("Reset")

  def manualEnable(self):
      x = 0
      self.door = 0
      self.lightOn()
      if self.menuline == 4: self.linactOn()
      elif self.menuline == 5: self.pwrsplyOn()
      elif self.menuline == 6: self.sonic1On()
      elif self.menuline == 7: self.sonic2On()
      lcd.lcd_clear()
      time.sleep(.1)
      if self.menuline == 4:  lcd.lcd_display_string(" Actuator Extended",1)
      elif self.menuline == 5: lcd.lcd_display_string("  Power Supply On",1) 
      elif self.menuline == 6: lcd.lcd_display_string("  Sonicator 1 On",1) 
      elif self.menuline == 7: lcd.lcd_display_string("  Sonicator 2 On",1) 
      lcd.lcd_display_string("     Press Knob",3) 
      if self.menuline == 4:  lcd.lcd_display_string("     to Retract",4) 
      else:                   lcd.lcd_display_string("    to Turn Off",4) 
      time.sleep(.5)
      while self.switch == 0:
          if self.door == 1:
              x = 1
              break
          time.sleep(.5)
      if self.menuline == 4: self.linactOff()
      elif self.menuline == 5: self.pwrsplyOff()
      elif self.menuline == 6: self.sonic1Off()
      elif self.menuline == 7: self.sonic2Off()
      self.lightOff()
      if x == 1:
          lcd.lcd_clear()
          time.sleep(.1)
          lcd.lcd_display_string("    Door Opened",2) 
          if self.menuline == 4 :  lcd.lcd_display_string("   Retracting...",3) 
          else:                   lcd.lcd_display_string("   Turning Off...",3) 
          time.sleep(3)
      self.menu()

  def autoRun(self):
      self.auto = 1
      print("Running")
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("     Running...",2) 
      time.sleep(1)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("Moving to Station 1",2) 
      step.step(271,1)
      self.position = 1
      jsn.writeJSON(self.sonictime, self.position)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("     Acid Bath",1) 
      self.pwrsplyOn()
      lcd.lcd_display_string("  Power Supply On",2) 
      time.sleep(1)
      self.linactOn()
      lcd.lcd_display_string(" Actuator Extended",3) 
      time.sleep(1)
      self.sonic1On()
      lcd.lcd_display_string("    Sonicator On",4) 
      self.reset()
      x = self.sonictime
      lcd.lcd_clear()
      time.sleep(.1)
      while x > 0:
          lcd.lcd_display_string("Time remaining:   "+str(x).zfill(2),1) 
          lcd.lcd_display_string("  Power Supply On",2) 
          lcd.lcd_display_string(" Actuator Extended",3) 
          lcd.lcd_display_string("    Sonicator On",4) 
          if self.door == 1: 
              lcd.lcd_clear()
              time.sleep(.1)
              lcd.lcd_display_string("     Door Ajar",2)
              lcd.lcd_display_string("    Aborting...",3)
              self.pwrsplyOff()
              self.linactOff()
              self.sonic1Off()
              self.doorAjar()
              self.pwrsplyOn()
              self.linactOn()
              self.sonic1On()
          x -= 1
          time.sleep(1)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("Acid Bath Complete",1) 
      self.pwrsplyOff()
      lcd.lcd_display_string("  Power Supply Off",2) 
      self.sonic1Off()
      lcd.lcd_display_string("   Sonicator Off",3) 
      self.linactOff()
      lcd.lcd_display_string("Actuator Retracted",4) 
      time.sleep(2)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("Moving to Station 2",2) 
      self.position = 2
      jsn.writeJSON(self.sonictime, self.position)
      step.step(140,0)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("   Water Station",1) 
      self.linactOn()
      lcd.lcd_display_string(" Actuator Extended",2) 
      self.sonic2On()
      lcd.lcd_display_string("    Sonicator On",3) 
      x = self.sonictime
      lcd.lcd_clear()
      time.sleep(.1)
      self.reset()
      while x > 0:
          lcd.lcd_display_string("   Water Station",1) 
          lcd.lcd_display_string(" Actuator Extended",2) 
          lcd.lcd_display_string("    Sonicator On",3) 
          lcd.lcd_display_string("Time Remaining:   "+str(x).zfill(2),4) 
          if self.door == 1:
              lcd.lcd_clear()
              time.sleep(.1)
              lcd.lcd_display_string("     Door Ajar",2)
              lcd.lcd_display_string("    Aborting...",3)
              self.pwrsplyOff()
              self.linactOff()
              self.sonic2Off()
              self.doorAjar()
              self.pwrsplyOn()
              self.linactOn()
              self.sonic2On()
          x -= 1
          time.sleep(1)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("Water Rinse Complete",1) 
      self.sonic2Off()
      lcd.lcd_display_string("   Sonicator Off",2) 
      self.linactOff()
      lcd.lcd_display_string("Actuator Retracted",3) 
      time.sleep(2)
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("   Returning Home",2) 
      self.position = 3
      jsn.writeJSON(self.sonictime, self.position)
      step.step(128,0)
      self.homing()
      print("Complete!")
      lcd.lcd_clear()
      time.sleep(.1)
      lcd.lcd_display_string("     Complete!",3) 
      time.sleep(2)
      self.button = 0 
      self.auto = 0
      self.ready()

if __name__== "__main__":
    try:
        acid = AcidDipTester()
        acid.boot()
    except KeyboardInterrupt:
        GPIO.cleanup()
        lcd.lcd_backlight("Off")
    print("Done")
