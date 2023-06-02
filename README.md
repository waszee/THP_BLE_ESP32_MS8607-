# THP_BLE_ESP32_MS8607- Temperature, Pressure, and Humidity -- ESP32C3 used for servers and Raspberry Pi used to run the Bluetooth LE client.

This project creastes two ESP32 servers.  Each is attached to a TE MS8607 sensor.  Each sensor returns the temperature, pressure, and humidity as characteristics values. 
The idea was to place one sensor inside and the other outside and let the client computer plot readings.  This should be useful for HVAC monitoring and help
monitor the environment in a house, lab, or other area.  The connections to the server are made via a wireless BLE client using Python BLEAK.   The sensors used the 
Adrafruit MS8607 library available in Arduino IDE code examples.  

The python client program runs on a raspberry Pi4 and should run under other platforms.  Both of the sensors are currently powered from USB lines attached to 
small chargers.  Hopefully will move to batteries and sensors that sleep between readings but that is a work in progress.  The client is currently not running 
on a  Win11 system after the latest May2023 system updates. Program did read the devices before the update and problem appears with the Window's drivers.  
The same code works on the linux Pi system.  The server uses the Adafruit library and the Arduino IDE.  A version was written using the ESP-IDF enhancement with 
Visual Studio Code but the RH sensor readings were not reliable although temperature and pressure were easily read.  
The Adrafruit library worked better for humidity readings but I am still have trouble with one of my sensors.  The ESP32C3 dev kit modules might be too fast 
for ho hold readings is my guess but still trying to determine what is issue. The problem might be just a loose connection. 

If you download the server you should replace the sensor characteristic UUIDs and the device servie UUID with your own UUIDS.   You will also need to modify the
server to give different each server a BLEname.  I noted the server addresses using the Nrf app on my cell phone.  That app is also useful to verify that the
ESP32 devices are returing the sensor characteristic values.  I also had to play around with the designated SDA and SCL pins on my sensors.  This was possible using 
Wire.begin(SDA,SCL) to start and set the pins for my devices before the program jumps to the MS8607 defaults.  If wire has already begun apparently the library does 
not try to modify.

I will try to post an update as improvements are made.  For example I know that I am not storing the CSV values correctly and not sure why using the import csv. 
Hopefully a simple fix.  
