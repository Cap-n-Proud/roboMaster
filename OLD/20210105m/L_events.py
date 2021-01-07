import json
import threading
import time
from datetime import datetime

from server import commandBuffer, dataJSON, sendArduinoCommand, serial_port


def pump():
    print("pump ON")
    time.sleep(2)
    print("pump OFF")


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]


def checkLights(currentProgram, dataJSON):
    global commandBuffer
    obj_now = datetime.now()
    timeNow = str(obj_now.hour).zfill(2) + ":" + str(obj_now.minute).zfill(2)
    # lights (RGB, brightness, timeON/OFF)
    # check if between light on timer
    if is_between(timeNow, currentProgram["lightsON"]):
        # print(dataJSON["brightness"])
        if dataJSON["brightness"] == 0:
            print("Lights should be ON")
            commandBuffer = "setBrightness " + str(currentProgram["lightBrightness"])
            # print(commandBuffer)
            # sendArduinoCommand("setLightRGB " + currentProgram["RGB"])
            # sendArduinoCommand(
            #     "setBrightness " + str(currentProgram["lightBrightness"])
            # )
            # sendArduinoCommand("statusReport")
            # read_from_port(serial_port)
            # dataJSON["brightness"] = str(currentProgram["lightBrightness"])
        # serial_port.write(str("setLightRGB " + "\n").encode())

    # Pump on/offghtRGB " duration, time


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
