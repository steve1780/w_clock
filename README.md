#   w_clock.py

## Wireless clock with MQTT Control

7-Segment display with max7219 driver chip to display time
in HH:MM:SS

MQTT is used to periodically update time in miropython-based board.
Can use ESP32, R-Pi RP2040 or other microprocessor. Original design
was going to use GPS to pull time data, but develoved into simpler
version.  This version uses MQTT to periodically update the HH:MM:SS
time by pulling time from the node-red server. The node-red server
can also be syncronized with NTP to provide correct time with an 
accuracy of 1 second.

## Notes

1. The program keeps the time in the micros RTC (if available)
2. An interval is set to request a re-sync with the server. This 
   refresh period is currently set to 1 hour
3. Reads environment variables with json file
4. Thinking about adding a time-set button to make the clock 
   indepentdent from MQTT.

   