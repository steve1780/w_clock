#====================================================================
# w_clock.py         7-Segment LED Clock with mqtt control
#
# scase   11/25/22    From node_timer.py programs 
#         03/14/25    Was node_clock2.py  in sandbox
#
#         03/14/25    Timeset branch          
#====================================================================

from umqtt.simple import MQTTClient
from machine import Pin, RTC, SoftSPI, Timer
import ubinascii
import time
import json
import network
import machine
import max7219

#----------------------------------------------------------------------#
# Pin definitions on GPS Clock board
#
# Pin 2 - Blue led on ESP32
# Pin 4 - On board yellow led
# Pin 23 - CS for SPI on MAX7219 LED board
# Pin 25 - TP1 Output pins
# Pin 26 - TP3
# Pin 27 - TP5 Using for timeset switch

ledB = Pin(2, Pin.OUT)
ledB.value(0)

ledY = Pin(4, Pin.OUT)
timeset = Pin(27, Pin.IN, Pin.PULL_UP)
ledY.value(1)

hours = 0
mins = 0
seconds = 0
times_up = 0
onthehour = False 
timeswFlag = False

#----------------------------------------------------------------------#
# Read json configuration file
#

with open('config.json') as fptr:
    config = json.load(fptr)
    
SERVER = config["server"]
SSID = config["ssid"]
PWD = config["password"]
pflag = config["printflag"]

print("Configuration : --------------------------------------- ")
print(config)

# Default MQTT server to connect to
CLIENT_ID = ubinascii.hexlify(machine.unique_id())

rtc = RTC()

# The real time clock keeps time used by the display
# The RTC is initialized by the server over MQTT messages, with the
# server time syncronized to NTP.
# The RTC time is re-syncronized by a one-hour timer requesting an update

#-------------------------------------------------------------------------#
def do_message(topic, msg):
    global hours
    global mins
    global seconds
    global pflag
    if pflag:
        print("Topic %s Message %s " % (topic, msg) )
   
    if b'ntpSEC' in topic :
        mess = str(msg, 'UTF-8')  
        seconds = int(float(mess))
    elif b'ntpMIN' in topic :
        mess = str(msg, 'UTF-8')  
        mins = int(float(mess))
    elif b'ntpHOUR' in topic :
        mess = str(msg, 'UTF-8')  
        hours = int(float(mess))
    else :
        print("Invalid MQTT command decode ")

    rtc.datetime((2022, 11, 11, 1, hours, mins, seconds,0))
        
          
#--------------------------------------------------------------------------#   
def sub_topic(TOPIC, pflag) :
    global server
    c.subscribe(TOPIC)
    if pflag :
        print("Connected to %s, subscribed to %s topic" % (server, TOPIC))        
   
    
#--------------------------------------------------------------------------#      
def init_display() :
# Clear the display and set a test pattern after boot
# display.clear()
  for i in list(range(1,9)):
    display.register(i, 0XF)   # this register instruction 0XF clears the
                               # digit at location i
  #time.sleep(1)
  for i in list((3, 6)):       # write the dashes on the dispay __-__-__
    display.register(i, 0xA)   # 0xA is the code for "-"
          
#-------------------------------------------------------------------------#
# These are the ISRs for the 1 second and hour timers
def flip_led(tim1):
  global times_up  			   # *** TODO - not sure if we need this
  if (not times_up) : 
    write_time()       
  else :
    init_display()
    

def hour_timer(tim2):
    global onthehour
    # set the onthehour flag so that RTC can be updated
    onthehour = True 

#-------------------------------------------------------------------------#
# take time units and place on clock digits
def write_time():
  global hours
  global seconds
  global mins
  global times_up
  t = rtc.datetime() # take the current time from the RTC
  seconds = t[6]     # 5th tuple is seconds
  mins = t[5]
  hours = t[4]
    
  if (seconds == 59) :
      seconds = 0
      mins += 1
  else :
     seconds += 1
     
  if (mins == 59) :
      mins = 0
      hours += 1
      if (hours > 23):
          hours = 0
  
  sec_tens = seconds // 10
  sec_units = seconds % 10
  min_tens = mins // 10
  min_units = mins % 10
  hour_tens = hours // 10
  hour_units = hours % 10
  display.register(8, hour_tens)
  display.register(7, hour_units)
  display.register(5, min_tens)
  display.register(4, min_units)
  display.register(2, sec_tens)
  display.register(1, sec_units)

def timesw(timeswitch):
   timeswFlag = True


# Initialization ------------------------------------------------------
#

time.sleep(0.5)
n=network.WLAN(network.STA_IF)
n.active(True)
n.connect(SSID,PWD)
while not n.isconnected() :
    time.sleep(1)


print("WLAN:", n.ifconfig())
server=SERVER
c = MQTTClient(CLIENT_ID, server)

# Subscribed messages will be delivered to a callback
c.set_callback(do_message)
c.connect()

sub_topic("ntpHOUR", 0)
sub_topic("ntpMIN", 0)
sub_topic("ntpSEC", 0)

# setup pin that is the control stobe for the display
cs = Pin(23, Pin.OUT)
cs.off()

# init the display object and the spi interface
spi = SoftSPI(baudrate=10000000, polarity=1, phase=0, sck=Pin(21), mosi=Pin(22),miso=Pin(13))
display = max7219.Max7219(spi, cs)

init_display()
tim1 = Timer(1)
tim2 = Timer(2)
c.publish(b"ntpREQ", b"request")  # trigger server to send update on HH:MM:SS

                               

tim1.init(period=1000, mode=Timer.PERIODIC, callback=flip_led)
tim2.init(period=3600000, mode=Timer.PERIODIC, callback=hour_timer)

timeset.Irq(timesw, trigger=Pin.IRQ_FALLING) # set callback for timeswitch


# Main loop -----------------------------------------------------------
#
while 1:
    print("*** in the inner loop ***")
    try:
        while 1:
          #micropython.mem_info()
          #print("in the inner loop")
          if onthehour :
              # flags are used becuase uPython is multi-threaded and putting
              # a MQTT request inside a callback is not advised
              
              c.publish(b"ntpREQ", b"request")
              print("RTC update requested")
              onthehour = False 
              
          c.check_msg()   

    finally:
        c.disconnect()

