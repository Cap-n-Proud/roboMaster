#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

import serial
#Initialize the serial port and
import serial.tools.list_ports
from flask import (Flask, jsonify, redirect, render_template, request, session,
                   url_for)

#https://stackoverflow.com/questions/24214643/python-to-automatically-select-serial-ports-for-arduino
ports = list(serial.tools.list_ports.comports())
for p in ports:
    print(p)

port = "/dev/ttyACM0"
baud = 115200

ser = serial.Serial(port, baud, timeout=1)
connected = False


app = Flask(__name__)
#NOTE: if the light is switched off it stays off until the next day
#This is the default route and main page of the app. Used to manage the programs and switch on and off lights activate the pump etc
@app.route('/')
def index():
    return render_template("index.html", progr=getProg(), currentProg=getCurrentProgr())

#API progtamming
@app.route('/program')
def program():

    return jsonify(getProg())

@app.route('/currentProgram')
def currentProgram():
    return jsonify(getCurrentProgr())

#This
# https://attacomsian.com/blog/using-javascript-fetch-api-to-get-and-post-data
@app.route('/postCommand',methods = ['POST', 'GET'])
def test():

    req = request.get_json()

    print(req['command'])

    # res = make_response(jsonify({"message": "OK"}), 200)

    return req

@app.route('/result',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
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


@app.route('/result2')
def result2():
    dict = {'phy': 50, 'che': 60, 'maths': 70}
    return render_template('result.html', result=dict)


@app.route('/guest/<guest>')
def hello_guest(guest):
    return 'Hello %s as Guest' % guest


@app.route('/user/<name>')
def hello_user(name):
    if name == 'admin':
        return redirect(url_for('hello_admin'))
    else:
        return redirect(url_for('hello_guest', guest=name))


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('success', name=user))
    else:
        user = request.args.get('nm')
        return redirect(url_for('success', name=user))


def getProg():
    with open("programs.json") as f:
      data = json.load(f)
    return data

def getCurrentProgr():
    with open("currentProgram.json") as f:
      data = json.load(f)
    return data

if __name__ == '__main__':
    print('Bla Bla Bla Bla Bla Bla Bla ')
    app.run(debug=True)
