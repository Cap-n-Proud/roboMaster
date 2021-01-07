import json
import threading
import time
from datetime import datetime

from server import sendArduinoCommand


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


def pump(runfFor, dataJSON):
    print("pump ON")
    time.sleep(runfFor)
    print("pump OFF")


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]


def checkLights(currentProgram, dataJSON):
    obj_now = datetime.now()
    timeNow = str(obj_now.hour).zfill(2) + ":" + str(obj_now.minute).zfill(2)
    # # lights (RGB, brightness, timeON/OFF)
    # # check if between light on timer, is_between accepts a list as second argument so we convert it
    if is_between(timeNow, list(currentProgram["lightsON"].split(","))) == True:
        if dataJSON["brightness"] == 0:
            print("Lights should be ON. Current value: ", dataJSON["brightness"])
            sendArduinoCommand(
                "setBrightness " + str(currentProgram["lightBrightness"])
            )
            sendArduinoCommand("setLightRGB " + str(currentProgram["RGB"]))
    else:
        print("Lights should be OFFCurrent value: ", dataJSON["brightness"])
    # Pump on/off duration, time


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
