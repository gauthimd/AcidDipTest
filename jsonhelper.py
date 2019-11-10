#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import json

class JSON():

    def __init__(self):
        self.sonictime = 0
        self.position = 0

    def writeJSON(self, sontime, position):
        update = {"sonictime": sontime,"position": position}
        with open('sonictime.json','w') as outfile:
            json.dump(update, outfile)
        outfile.close()
    
    def readJSON(self):
        sonictime = 0
        with open('sonictime.json') as infile:
            data = json.load(infile)
        infile.close()
        self.sonictime = data["sonictime"]
        self.position = data["position"]
        return self.sonictime, self.position

if __name__=="__main__":
    j = JSON()
    j.writeJSON(10,2)
    sonictime,position = j.readJSON()
    print(sonictime,position)
    print(type(sonictime),type(position))
