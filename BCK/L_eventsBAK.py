import json
import threading
import time
from datetime import datetime


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.next_call = time.time()
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


def lightsSwitch():  # user defined function which adds +10 to given number
    print("Hey u called me")
    print(is_between(timeNow, ("09:00", "02:00")))  # True


def pump():
    print("pump ON")
    time.sleep(2)
    print("pump OFF")


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]


def getCurrentProgr():
    with open("currentProgram.json") as f:
        data = json.load(f)
    return data


def checkTimers(currentProgram):
    obj_now = datetime.now()
    timeNow = str(obj_now.hour).zfill(2) + ":" + str(obj_now.minute).zfill(2)
    # lights (RGB, brightness, timeON/OFF)
    # check if between light on timer
    print(currentProgram["lightsON"])
    if is_between(timeNow, currentProgram["lightsON"]):
        print("AA")
    # Pump on/off duration, time


delay = 3

currentProgram = getCurrentProgr()

rt = RepeatedTimer(delay, lightsSwitch)  # it auto-starts, no need of rt.start()
pumpContol = RepeatedTimer(5, pump)  # it auto-starts, no need of rt.start()
checkT = RepeatedTimer(
    1, checkTimers, currentProgram
)  # it auto-starts, no need of rt.start()

obj_now = datetime.now()

print("Current hour =", str(obj_now.hour).zfill(2))
print("Current minute =", str(obj_now.minute).zfill(2))
print("Current second =", str(obj_now.second).zfill(2))

timeNow = str(obj_now.hour).zfill(2) + ":" + str(obj_now.minute).zfill(2)
print(timeNow)
print(is_between(timeNow, ("09:00", "02:00")))  # True
for x in range(0, 100):
    print(x)
    time.sleep(1)

rt.stop()


"""
{ "progName": "This is the current program",
  "pumpStartEvery": 60,
  "pumpRunTime": 5,
  "pumpStopHours":"20:00, 04:00",
  "lightBrightness": 80,
  "RGB": "10 100 210",
  "lightsON":"04:00, 20:00"
}

{"type":"T","pumpON":false,"RGB":null,"brightness":0,"PH":0,"waterLevel":0}

"""
