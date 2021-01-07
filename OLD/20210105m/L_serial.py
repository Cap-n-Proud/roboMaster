import threading
import time

import serial
import server
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


def handle_data(data):
    print(data)
    if data[:1] == "I":
        print("INFO RECEIVED")
        server.broadcastInfo(data)


def read_from_port(ser):
    while True:
        # NB: for PySerial v3.0 or later, use property `in_waiting` instead of function `inWaiting()` below!
        if (
            ser.in_waiting > 0
        ):  # if incoming bytes are waiting to be read from the serial input buffer
            data_str = ser.readline(ser.in_waiting + 30).decode(
                "ascii"
            )  # read the bytes and convert from binary array to ASCII
            # print(data_str, end='') #print the incoming string without putting a new-line ('\n') automatically after every print()
            handle_data(data_str.strip("\n").strip("\c"))
    # time.sleep(0.1)


def write_to_ser(ser, message):
    ser.write(str(message + "\n\c").encode())


thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()

# while True:
#     print(read_all(serial_port))
#
# thread = threading.Thread(target=read_all, args=(serial_port,200))
# thread.start()
print("serial interface configured. Pyserisal version: " + serial.VERSION)
time.sleep(2)
# write_to_ser(serial_port,"help")
# write_to_ser(serial_port,"setLightRGB 255 0 255")
