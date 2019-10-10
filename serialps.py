#!/usr/bin/python
# -*- encoding: utf-8 -*-

import time
import serial

class powerSupply():

    def __init__(self, volts=24, amps=4):
        self.ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        self.ser.write(b"*IDN?"+b"\n")
        x = self.ser.read(100)
        print(x.strip())
        self.volts = bytes(str(volts))
        self.ovp = bytes(str(int(self.volts) + 1))
        self.amps = bytes(str(amps))
        self.ocp = bytes(str(int(self.amps) + .25))
        time.sleep(1)

    def lockKeys(self):
        self.ser.write(b":SYSTem:LOCK 1"+b"\n")
        print("Keypad Locked")
        time.sleep(1)
        
    def unlockKeys(self):
        self.ser.write(b":SYSTem:LOCK 0"+b"\n")
        print("Keypad Unlocked")
        time.sleep(1)

    def setVoltsAmps(self):
        self.ser.write(b"APPLy CH1,"+self.volts+","+self.amps+b"\n")
        print("Voltage and Current Set")
        time.sleep(1)

    def setProtection(self):
        self.ser.write(b"OUTPut:OCP:VALue "+self.ocp+b"\n")
        time.sleep(1)
        self.ser.write(b"OUTPut:OCP:STATe CH1,ON"+b"\n")
        print("OCP Set")
        time.sleep(1)
        self.ser.write(b"OUTPut:OVP:VALue "+self.ovp+b"\n")
        time.sleep(1)
        self.ser.write(b"OUTPut:OVP:STATe CH1,ON"+b"\n")
        print("OVP Set")
        time.sleep(1)

    def turnOn(self):
        self.ser.write(b"OUTPut:STATe CH1,ON"+b"\n")
        print("Output On")
        time.sleep(1)
    
    def turnOff(self):
        self.ser.write(b"OUTPut:STATe CH1,OFF"+b"\n")
        print("Output Off")
        time.sleep(1)

    def selfCheck(self):
        print("Status Check")
        z = 1
        volts=0
        amps=0
        watts=0
        self.ser.write(b":MEASure:ALL? CH1"+b"\n")
        x = self.ser.read(100)
        for y in x.split(','):
            if z==1: volts = y
            elif z==2: amps = y
            else: watts = y
            z+=1
        v = float(volts)
        i = float(amps)
        w = float(watts)
        print("Volts = "+ volts + " V")
        print("Amps = " + amps + " amps")
        print("Watts = " + watts.strip() + " W")
        time.sleep(1)
        if v > float(self.volts) or i > float(self.amps): return 1
        else: return 0

    def close(self):
        self.ser.close()
        print("Serial Port Closed")
        time.sleep(1)

if __name__=="__main__":
    power = powerSupply(15,3)
    power.lockKeys()
    power.setVoltsAmps()
    power.setProtection()
    power.turnOn()
    if power.selfCheck()==1: print("It's fucked")
    else: print("It's good")
    time.sleep(5)
    power.turnOff()
    power.unlockKeys()
    power.close()
    print("Done")
