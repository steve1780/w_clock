#   w_clock.py

## Wireless clock with MQTT Control

7-Segment display with max7219 driver chip to display time
in HH:MM:SS is kept syncronized with NTP over the net.

MQTT is used to periodically update time in micropython-based board.
Can use ESP32, Raspberry-Pi Pico or other microprocessor. Original design
was going to use GPS to pull time data, but devolved into simpler
version. GPS module would have been used to provide PPS signals for
10 MHz lab timebase. 

Primary time-sync is through NTP time pool servers. This polling occurs
once every hour. The MicroPython ntptime library does all the heavy lifting.
This guarantees that we have at least 1s accuracy for a while. We can also 
use MQTT to act as a backup to update time from the node-red server.
The node-red server can also be syncronized with NTP.

Added MQTT topic for GMTOFFSET so that time zone corrections can be easily
updated.

## Notes

1. The program keeps the time in the micros RTC which is standard on the ESP32.
2. An interval is set to request a re-sync with the server. This refresh period
   is currently set to 1 hour
3. Reads environment variables with json file. Environment includes GMT offset.
4. Time-Set Feature. We were thinking about a time-set feature, but since this 
   project relys on network connectivity, we opted for simplifying with NTP pool
   sync and optional mqtt/node-red pub/sub updates.
5. MicroPython-based boards require WiFi for MQTT server communication.   
