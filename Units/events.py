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

def fun():         # user defined function which adds +10 to given number

    print ("Hey u called me")
    print(is_between(timeNow, ("09:00", "02:00")))  # True


def punp():
    print("pump ON")
    time.sleep(2)
    print("pump OFF")


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]

delay = 3

rt = RepeatedTimer(delay, fun) # it auto-starts, no need of rt.start()
rtp = RepeatedTimer(5, punp) # it auto-starts, no need of rt.start()

obj_now = datetime.now()
print("Current hour =", str(obj_now.hour).zfill(2))
print("Current minute =", str(obj_now.minute).zfill(2))
print("Current second =", str(obj_now.second).zfill(2))

timeNow = str(obj_now.hour).zfill(2) + ':' + str(obj_now.minute).zfill(2)
print(timeNow)
print(is_between(timeNow, ("09:00", "02:00")))  # True
for x in range (0, 100):
    print(x)
    time.sleep(1)

rt.stop()
