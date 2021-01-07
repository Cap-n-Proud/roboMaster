import json
import threading
import time
from datetime import datetime
from threading import Lock, Thread

import serial

a = 0  # global variable

commandBuffer = "N/A"

# import serial
dataJSON = {
    "type": "T",
    "pumpON": False,
    "RGB": "0 0 0",
    "brightness": 0,
    "PH": 0,
    "waterLevel": 0,
}


def serT(threadname):
    global commandBuffer
    global dataJSON
    port = "/dev/ttyACM0"
    baud = 115200

    ser = serial.Serial(port, baud, timeout=0.5)
    print("serial interface configured. Pyserisal version: " + serial.VERSION)
    time.sleep(2)
    while True:
        print("ser_T Treiggered " + commandBuffer)
        if (
            ser.in_waiting > 0
        ):  # if incoming bytes are waiting to be read from the serial input buffer
            data_str = ser.readline(ser.in_waiting + 300)
            print(data_str)
            try:
                # global dataJSON
                dataJSON = json.loads(data_str.decode())
            except ValueError as e:
                print("NOT JSON: ")
                print(data_str)
        if commandBuffer != "N/A":
            ser.write(str(commandBuffer + "\n").encode())
            print("WROTE!!! " + commandBuffer)
            commandBuffer = "N/A"


def checkStatus(threadname):
    global commandBuffer
    while True:
        commandBuffer = "statusReport"
        print("status checked ", commandBuffer)
        time.sleep(3)


def thread2(threadname):
    global a
    while 1:
        a += 1
        time.sleep(1)


thread1 = Thread(target=serT, args=("Thread-1",))
thread2 = Thread(target=checkStatus, args=("Thread-2",))
thread1.start()
thread2.start()
#
# thread1.join()
# thread2.join()
