import json

class JSON():

    def __init__(self):
        self.sonictime = 0

    def writeJSON(self,sontime):
        update = {"sonictime": sontime}
        with open('sonictime.json','w') as outfile:
            json.dump(update, outfile)
        outfile.close()
    
    def readJSON(self):
        sonictime = 0
        with open('sonictime.json') as infile:
            data = json.load(infile)
        infile.close()
        self.sonictime = data["sonictime"]
        return self.sonictime

if __name__=="__main__":
    j = JSON()
    j.writeJSON(10)
    sonictime = j.readJSON()
    print(sonictime)
    print(type(sonictime))
