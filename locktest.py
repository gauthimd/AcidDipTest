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

class Pauser():

    def lockThread(self):
        print("Start lock")
        lock.paused = True
        lock.pause_cond.acquire()
        time.sleep(5)
        print("End lock")

    def releaseLock(self):
        print("Start release")
        lock.paused = False
        lock.pause_cond.notify()
        lock.pause_cond.release()
        print("End release")

    def startThread(self):
        t1 = threading.Thread(target=lock.counter)
        t1.daemon
        t1.start()
        return t1

    def stopThread(self,t1):
        t1.do_run = False
        t1.join()

if __name__=="__main__":
    lock = Lock()
    pause = Pauser()
    th = pause.startThread()
    time.sleep(3)
    pause.lockThread()
    pause.releaseLock()
    time.sleep(8)
    pause.stopThread(th)
