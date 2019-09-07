#!/usr/bin/python3
# -*- encoding: utf-8 -*-

from datetime import datetime
import KY040, lcddriver, time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)

lcd = lcddriver.lcd()
rot = KY040.KY040(21,20,24)

class menu():

    def __init__(self):
        self.stringdict = {1:"",2:"",3:"",4:""}
        self.blinkline = 1
        self.blinkon = 0
        self.button = 0
        self.lcd = lcddriver.lcd()
        self.rot = KY040.KY040(21,20,24,self.rotarycallback,self.switchcallback)
        self.rot.start()

    def hello(self):
        for x in self.stringdict:
            self.stringdict[x] = "Hello"
        self.lcd.lcd_clear()
        z = 0
        while True:
            if self.blinkon == 1:
                for x in self.stringdict:
                    if x == self.blinkline:
                        if z == 1:
                            self.lcd.lcd_display_string(self.stringdict[self.blinkline],self.blinkline)
                            z = 0
                        else: 
                            self.lcd.lcd_display_string("",self.blinkline)
                            z = 1
                    else:
                        self.lcd.lcd_display_string(self.stringdict[x],x)
                time.sleep(.5)
                self.lcd.lcd_clear()
            else: 
                for x in self.stringdict:
                    self.lcd.lcd_display_string(self.stringdict[x],x)
                time.sleep(.5)
        self.lcd.lcd_clear()

    def rotarycallback(self,direction):
        if self.blinkon == 1:
            if direction == 0: 
                self.blinkline +=1
                if self.blinkline > 4: self.blinkline = 1
            else:
                self.blinkline -=1
                if self.blinkline < 1: self.blinkline = 4
        print(self.blinkline)

    def switchcallback(self):
        print("Button pressed")
        if self.blinkon == 0: self.blinkon = 1
        else: self.blinkon = 0

    def run(self):
        try:
            self.hello()
        except KeyboardInterrupt:
            self.rot.stop()
            GPIO.cleanup()

if __name__=="__main__":
    menu = menu()
    menu.run()
