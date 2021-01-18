#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import logging
import threading
import time
from threading import Lock

import serial
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, disconnect, emit
from L_events import *
from serial.tools import list_ports

app = Flask(__name__)
app.debug = True

logging.basicConfig(
    filename="record.log",
    level=logging.DEBUG,
    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)
# see last post to fix github issues: https://stackoverflow.com/questions/23344320/there-isnt-anything-to-compare-nothing-to-compare-branches-are-entirely-diffe
# We log the following events:
# -Pump ON
# -Pump OFF
# -Lights ON
# -Lights OFF
# -RGB Changed

dataJSON = ""

# TODO ADD logging, debug, test teh system and add features to the interface (e.g.: current status )

# https://stackoverflow.com/questions/17553543/pyserial-non-blocking-read-loop#38758773
# https://stackoverflow.com/questions/19161768/pyserial-inwaiting-returns-incorrect-number-of-bytes#47614497
# https://stackoverflow.com/questions/24214643/python-to-automatically-select-serial-ports-for-arduino
port = "/dev/ttyACM0"
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

# print(port.split("/")[2])
baud = 115200

serial_port = serial.Serial(port, baud, timeout=0.5)

print("serial interface configured. Pyserisal version: " + serial.VERSION)
time.sleep(2)


# Suppress logging
import logging

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

async_mode = None
thread = None

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_mode=async_mode)


@app.route("/")
def index():
    return render_template(
        "index.html",
        async_mode=socketio.async_mode,
        progr=getProg(),
        currentProg=getCurrentProgr(),
    )


@app.route("/status")
def status():
    return render_template(
        "status.html", async_mode=socketio.async_mode, plants=getPlants(),
    )


# API programming
# Get list of programs as JSON
@app.route("/api/programs")
def program():
    return jsonify(getProg())


# Get current program as JSON
@app.route("/api/currentProgram")
def currentProgram():
    return jsonify(getCurrentProgr())


# Get plants as JSON
@app.route("/api/getPlants")
def getP():
    return jsonify(getPlants())


# Get current status as JSON
@app.route("/api/s")
def getStatus():
    return jsonify(getStatus())


# https://attacomsian.com/blog/using-javascript-fetch-api-to-get-and-post-data
# Post a command to the arduino via web interface like swith pump on or off, lights etc
@app.route("/arduinoCommand", methods=["POST", "GET"])
def arduinoCommand():

    req = request.get_json()

    print(req["command"])
    # L_serial.serial_port.write_to_ser(L_serial.serial_port, req['command']);
    serial_port.write(str(req["command"] + "\n").encode())
    # res = make_response(jsonify({"message": "OK"}), 200)
    return render_template("index.html", progr=getProg(), currentProg=getCurrentProgr())


# https://attacomsian.com/blog/using-javascript-fetch-api-to-get-and-post-data
# Post a command to the arduino via web interface like swith pump on or off, lights etc
@app.route("/api/plant", methods=["POST", "GET"])
def p():
    req = request.get_json()
    print(req)

    with open("status.json", "r") as f:
        data = json.load(f)
        try:
            newPlant = req["plantName"]
            l = req["podID"].split("-")
            currentPod = data["towers"][int(l[0])]["levels"][int(l[1])]["pods"][
                int(l[2])
            ]
            print(currentPod["plantName"])
            currentPod["plantName"] = req["plantName"]
            currentPod["plantID"] = req["plantID"]
            currentPod["plantedDate"] = req["plantedDate"]
            json.dump(data, open("status.json", "w"), indent=4)
            I = (
                "Planted: "
                + currentPod["plantID"]
                + " "
                + newPlant
                + " in "
                + req["podID"]
            )
            app.logger.info(I)
            broadcastInfo(I)
        except Exception as e:
            print(e)

    return render_template(
        "status.html", async_mode=socketio.async_mode, plants=getPlants(),
    )


# Post a command to the server, not really used for now
@app.route("/serverCommand", methods=["POST", "GET"])
def serverCommand():
    if request.method == "POST":
        result = request.form
        # Validate the request body contains JSON
        if request.is_json:

            # Parse the JSON into a Python dictionary
            req = request.get_json()
            # print(req)

            # Return a string along with an HTTP status code
            return "JSON received!", 200
        else:

            print("NOT JSON")
            # The request body wasn't JSON so return a 400 HTTP status code
            return "Request was not JSON", 400
    return render_template("index.html", progr=getProg(), currentProg=getCurrentProgr())


# Sends the current program to Arduino, used as a test for the web interface
def sendProgramToArduino():
    data = getCurrentProgr()
    # serial_port.write(
    #     str("setBrightness " + str(data["lightBrightness"]) + "\n").encode()
    # )
    time.sleep(0.1)
    serial_port.write(str("setLightRGB " + str(data["RGB"]) + "\n").encode())


@socketio.on("sendProgram")
def sp():
    sendProgramToArduino()


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected", request.sid)


# Retrieve the list of programs, used to populate the indey.html file
def getProg():
    with open("programs.json") as f:
        data = json.load(f)
    return data


def getStatus():
    with open("status.json") as f:
        data = json.load(f)
    return data


# Retrieve the current program, used to populate the indey.html file
def getCurrentProgr():
    with open("currentProgram.json") as f:
        data = json.load(f)
    return data


def getPlants():
    with open("plants.json") as f:
        data = json.load(f)
    return data


# Broadcast info to every client
def broadcastInfo(data):
    socketio.emit("info", data)
    print(data + " sent")


def handle_data(data):
    global dataJSON
    try:
        dataJSON = json.loads(data.decode())
        if dataJSON["type"] == "I":
            broadcastInfo(dataJSON["message"])
            app.logger.info("Info from Arduino: " + dataJSON["message"])

        if dataJSON["type"] == "T":
            print(dataJSON)
            socketio.emit("telemetry", dataJSON)

    except ValueError as e:
        app.logger.warning("Received non-JSON from Arduino: " + str(data))
        print(data)


def read_from_port(ser):
    while True:
        # NB: for PySerial v3.0 or later, use property `in_waiting` instead of function `inWaiting()` below!
        if (
            ser.in_waiting > 0
        ):  # if incoming bytes are waiting to be read from the serial input buffer
            data_str = ser.readline(ser.in_waiting + 300)
            # read the bytes and convert from binary array to ASCII
            handle_data(data_str)


def write_to_ser(ser, message):
    ser.write(str(message + "\n\c").encode())


# Setup and start the thread to read serial port
thread_lock = Lock()
thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()

# Send command to Arduino, used for python calls
def arduinoCommand2(command):
    serial_port.write(str(command + "\n").encode())
    time.sleep(0.5)


def background_thread():
    """Example of how to send server generated events to clients. to be set as a thread"""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit("my_response", {"data": "Server generated event", "count": count})


# Calculate if a time is between a time range (specified as list)
def is_between(startTime, endTime, nowTime):
    endTime = datetime.strptime(endTime, "%H:%M")
    startTime = datetime.strptime(startTime, "%H:%M")
    nowTime = datetime.strptime(nowTime, "%H:%M")

    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:  # Over midnight
        return nowTime >= startTime or nowTime <= endTime


# This will be called to regulate the pump behaviour. TODO need to add thread and parameterd
def checkPump(duration):
    obj_now = datetime.now()
    timeNow = str(obj_now.hour).zfill(2) + ":" + str(obj_now.minute).zfill(2)
    if is_between(currentProgram["pumpON"], currentProgram["pumpOFF"], timeNow):
        print("pump ON")
        arduinoCommand2("pumpStart")
        app.logger.info("Pump is ON")
        # We stop the thread so the pump continues pumping
        time.sleep(duration)
        print("pump OFF")
        arduinoCommand2("pumpStop")
        app.logger.info("Pump is OFF")


# Function to check the lights. If we are in the time range it will switch the light on and give the current proram RGB color
# TODO when teh web UI set pump to off it returns an error (even with the try statement)
def checkLights(currentProgram):
    obj_now = datetime.now()
    timeNow = str(obj_now.hour).zfill(2) + ":" + str(obj_now.minute).zfill(2)
    # lights (RGB, brightness, timeON/OFF)
    # check if between light on timer
    if is_between(currentProgram["lightsON"], currentProgram["lightsOFF"], timeNow):
        try:
            test = dataJSON["brightness"]

            if dataJSON["brightness"] == 0:  # print("Lights should be ON")
                arduinoCommand2(
                    "setBrightness " + str(currentProgram["lightBrightness"])
                )
                arduinoCommand2("setLightRGB " + str(currentProgram["RGB"]))
                print("Brightness set to default")
                app.logger.info("Lights ON, RGB also set")

        except ValueError as e:
            print(e)
    else:
        if dataJSON["brightness"] != 0:  # print("Lights should be ON")
            arduinoCommand2("setBrightness 0")
            app.logger.info("Lights OFF, RGB also set")


if __name__ == "__main__":
    currentProgram = getCurrentProgr()

    # print(currentProgram["progName"])
    # print(currentProgram["pumpStartEvery"])
    # print(currentProgram["lightBrightness"])
    # print(currentProgram["RGB"])

    checkL = RepeatedTimer(
        1, checkLights, currentProgram
    )  # it auto-starts, no need of rt.start()
    checkP = RepeatedTimer(
        currentProgram["pumpStartEvery"], checkPump, currentProgram["pumpRunTime"]
    )  # it auto-starts, no need of rt.start()
    obj_now = datetime.now()
    timeNow = str(obj_now.hour).zfill(2) + ":" + str(obj_now.minute).zfill(2)
    print("Current hour =", str(obj_now.hour).zfill(2))
    print("Current minute =", str(obj_now.minute).zfill(2))
    print("Current second =", str(obj_now.second).zfill(2))
    print(timeNow, currentProgram["lightsON"])
    print(is_between(currentProgram["lightsON"], currentProgram["lightsOFF"], timeNow))
    print(is_between(currentProgram["pumpON"], currentProgram["pumpOFF"], timeNow))
    # checkT.stop()
    socketio.run(app)

"""
{
  "progName": "This is the current program",
  "pumpStartEvery": 2400,
  "pumpRunTime": 300,
  "pumpON": "08:00",
  "pumpOFF": "23:00",
  "lightBrightness": 80,
  "RGB": "200 100 200",
  "lightsON": "04:00",
  "lightsOFF": "20:00"
}
"""
