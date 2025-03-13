# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
from machine import Pin
import time
led = Pin(2, Pin.OUT)
for i in range(3) :
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)
    
print("Boot Delay")
time.sleep(5)

#import gps_clock_dev
import  w_clock.py


