import threading, time

class Lock(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.paused = False
        self.pause_cond = threading.Condition(threading.Lock())
        print("__init__ done")

    def counter(self):
        print("Start counter")
        x = 0
        while x < 10:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
                print(x)
                x+= 1
            time.sleep(1)
        print("Done")
