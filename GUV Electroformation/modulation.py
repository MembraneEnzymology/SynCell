#!/usr/bin/python3

"""
This program modulates the PSG9080

- turn both channels off
- set frequency to 500 Hz and amplitude to 150mV
- initially wait for 60 seconds
- turn both channels on
- ramp voltage to 3.9V in 30 minutes
- keep voltage at 3.9V for 1,5 hours
- turn both channels off

Rijksuniversiteit Groningen, 2022
C.M. Punter (c.m.punter at rug.nl)
J. Coenradij (j.counradij at rug.nl)

"""


import serial
import re
import threading 
import time
import os

# change the following parameters if needed
port = "/dev/ttyUSB0"     # change this if needed
frequency = 500           # in herz
initial_wait = 60         # 1 minute
duration_ramp = 30 * 60   # 30 minutes
duration = 2 * 60 * 60    # 2 hours
start_voltage = 0.150     # 150 mV
end_voltage = 3.9         # 3.9 V
update_interval = 1       # update every second

class PSG9080:
    def __init__(self, port):
        self.ser = serial.Serial(port=port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, xonxoff=1)
        #self.read() # AT.
        #self.read() # AT.
        #self.read() # AT+NAME=BSG536
        self.pattern = re.compile(":r(\d\d)=(\d+(?:,\d+)*)\.")
        
    def get_parameters(self):
        parameters = []
        self.write(":r00=90.")
        for i in range(91):
            m = self.pattern.match(self.read())
            parameters.append(m.group(2))
        return parameters
            
    def read(self) -> str:
        b = bytes()
        ch = 0
        while ch != b'\n':
            ch = self.ser.read()
            b += ch
        return b[:-2].decode("ascii")

    def write(self, s: str):
        self.ser.write(s.encode("ascii") + b'\r\n')
    
    def close(self):
        self.ser.close()

    def set_amplitude(self, voltage: float, channel: int=1) -> bool:
        self.write(":w%02d=%d." % (14 + channel, int(voltage * 1000)))
        return self.read() == ":ok"
        
    def set_frequency(self, frequency: float, channel: int=1) -> bool:
        self.write(":w%02d=%d." % (12 + channel, int(frequency * 1000)))
        return self.read() == ":ok"
    
    def enable_channels(self):
        self.write(":w10=1,1.")
        return self.read() == ":ok"
        
    def disable_channels(self):
        self.write(":w10=0,0.")
        return self.read() == ":ok"

# https://www.alixaprodev.com/2022/07/how-to-execute-function-every-x-seconds.html
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

def update(start_time: float):
    run_time = (time.time() - start_time)
    
    if run_time <= duration_ramp:
        voltage = start_voltage + ((end_voltage - start_voltage) * run_time) / duration_ramp
    else:
        voltage = end_voltage
        
    #print("%.2fs %6.3fV\r" % (run_time, voltage), end="")
    psg9080.set_amplitude(voltage, 1)
    psg9080.set_amplitude(voltage, 2)

# wait until /dev/ttyUSB0 exists
while not os.path.exists(port):
    time.sleep(5)

psg9080 = PSG9080(port)
psg9080.disable_channels()

# set both channels to 0.150V and 500Hz
psg9080.set_amplitude(start_voltage, 1)
psg9080.set_amplitude(start_voltage, 2)
psg9080.set_frequency(frequency, 1)
psg9080.set_frequency(frequency, 2)

time.sleep(initial_wait)
psg9080.enable_channels()

# do ramp
start_time = time.time()
rep = RepeatedTimer(update_interval, update, (start_time))
rep.start()

# wait for ramp to complete
time.sleep(duration_ramp)
rep.stop()

# set to final voltage
psg9080.set_amplitude(end_voltage, 1)
psg9080.set_amplitude(end_voltage, 2)

# wait for full duration
time.sleep(duration - (time.time() - start_time))

# disable channels
psg9080.disable_channels()

# close connection since we completed the modulation
psg9080.close()
    
