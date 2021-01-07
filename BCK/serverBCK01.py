#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import threading
import time
from threading import Lock

import serial

# Initialize the serial port and
# import serial.tools.list_ports
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, disconnect, emit
from L_events import *
from serial.tools import list_ports

# https://stackoverflow.com/questions/17553543/pyserial-non-blocking-read-loop#38758773
# https://stackoverflow.com/questions/19161768/pyserial-inwaiting-returns-incorrect-number-of-bytes#47614497

# https://stackoverflow.com/questions/24214643/python-to-automatically-select-serial-ports-for-arduino
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

port = "/dev/ttyACM0"
baud = 115200

serial_port = serial.Serial(port, baud, timeout=0.5)

# while True:
#     print(read_all(serial_port))
#
# thread = threading.Thread(target=read_all, args=(serial_port,200))
# thread.start()
print("serial interface configured. Pyserisal version: " + serial.VERSION)
time.sleep(2)

app = Flask(__name__)
# NOTE: if the light is switched off it stays off until the next day
# This is the default route and main page of the app. Used to manage the programs and switch on and off lights activate the pump etc

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


# API programming
# Get list of programs as JSON
@app.route("/programs")
def program():
    print("Programs called")
    return jsonify(getProg())


# Get current program as JSON
@app.route("/currentProgram")
def currentProgram():
    return jsonify(getCurrentProgr())


# https://attacomsian.com/blog/using-javascript-fetch-api-to-get-and-post-data
# Post a command to the arduino like swith pump on or off, lights etc
@app.route("/arduinoCommand", methods=["POST", "GET"])
def arduinoCommand():

    req = request.get_json()

    print(req["command"])
    # L_serial.serial_port.write_to_ser(L_serial.serial_port, req['command']);
    serial_port.write(str(req["command"] + "\n").encode())
    # res = make_response(jsonify({"message": "OK"}), 200)
    return render_template("index.html", progr=getProg(), currentProg=getCurrentProgr())


# Post a command to the server
@app.route("/serverCommand", methods=["POST", "GET"])
def serverCommand():
    if request.method == "POST":
        result = request.form
        # Validate the request body contains JSON
        if request.is_json:

            # Parse the JSON into a Python dictionary
            req = request.get_json()
            print(req)

            # Return a string along with an HTTP status code
            return "JSON received!", 200
        else:

            print("NOT JSON")
            # The request body wasn't JSON so return a 400 HTTP status code
            return "Request was not JSON", 400
    return render_template("index.html", progr=getProg(), currentProg=getCurrentProgr())


@socketio.event
def my_ping():
    emit("my_pong")
    print("PING")


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit("my_response", {"data": "Connected", "count": 0})


def sendProgramToArduino():
    data = getCurrentProgr()
    serial_port.write(
        str("setBrightness " + str(data["lightBrightness"]) + "\n").encode()
    )
    time.sleep(0.1)
    serial_port.write(str("setLightRGB " + str(data["RGB"]) + "\n").encode())
    print("Program sent")


@socketio.on("sendProgram")
def sp():
    sendProgramToArduino()
    print("prgram sent to arduino")


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected", request.sid)


# Retrieve the list of programs, used to populate the indey.html file
def getProg():
    with open("programs.json") as f:
        data = json.load(f)
    return data


# Retrieve the current program, used to populate the indey.html file
def getCurrentProgr():
    with open("currentProgram.json") as f:
        data = json.load(f)
    return data


def broadcastInfo(data):
    socketio.emit("info", data)
    print(data + " sent")


def handle_data(data):
    d = "JSONFILE"
    # d = json.loads(data)
    print(data)
    print("DATA")
    if d["type"] == "I":
        broadcastInfo(data)
    if d["type"] == "T":
        broadcastInfo(data)


def read_from_port(ser):
    while True:
        # NB: for PySerial v3.0 or later, use property `in_waiting` instead of function `inWaiting()` below!
        if (
            ser.in_waiting > 0
        ):  # if incoming bytes are waiting to be read from the serial input buffer
            data_str = ser.readline(ser.in_waiting + 300).decode(
                "ascii"
            )  # read the bytes and convert from binary array to ASCII
            # print(data_str, end='') #print the incoming string without putting a new-line ('\n') automatically after every print()
            handle_data(data_str.strip("\n").strip("\c"))
    # time.sleep(0.1)


def write_to_ser(ser, message):
    ser.write(str(message + "\n\c").encode())


thread_lock = Lock()

thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit("my_response", {"data": "Server generated event", "count": count})


if __name__ == "__main__":
    currentProgram = getCurrentProgr()

    checkT = RepeatedTimer(
        1, checkTimers, currentProgram
    )  # it auto-starts, no need of rt.start()
    obj_now = datetime.now()
    print("Current hour =", str(obj_now.hour).zfill(2))
    print("Current minute =", str(obj_now.minute).zfill(2))
    print("Current second =", str(obj_now.second).zfill(2))

    # checkT.stop()

    socketio.run(app)
