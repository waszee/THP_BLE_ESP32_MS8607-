# THP_BLE_ESP32_MS8607- Temperature, Pressure, and Humidity -- ESP32C3 used for servers and Raspberry Pi used to run the Bluetooth LE client.

This project connects two ES932 microcontrollers with temperature, humidity, and pressure sensors to monitoring computer system via Bluetooth low energy.  In the initial
applicatiion TE MS8607 sensors where used.  Later development will evaluate the BME 280 and 680 sensors as well as remote thermocouple. 

The idea was to place one sensor inside and the other outside and let the client computer plot readings.  This should be useful for HVAC monitoring and help
monitor the environment in a house, lab, or other area.  The connections to the server are made via a wireless BLE client using Python BLEAK.   The sensors used the 
Adrafruit MS8607 library available in Arduino IDE code examples.  

The python client program runs on a raspberry Pi4 and should run under other platforms.  Both of the sensors are currently powered from USB lines attached to 
small chargers.  Hopefully will move to batteries and sensors that sleep between readings but that is a work in progress.  

To get the monitoring program to run on Windows 11 computer the python code needed to be broken into two modules.  One modules retrieves the readings from the sensors using
asynchronous calls.  That module then calls a child module to plot the data and pipes the current readings to the child to append to a plot of the data.  This approach is shown in
the THP_Data2wBuf.py and simple_fileread_dataPlot.py modules. 

The ESP32C3 microcontroller uses the Adafruit library and the Arduino IDE with esp32 extensions.  Another ESP32 controller was written using the ESP-IDF enhancement with 
Visual Studio Code but the RH sensor readings were not reliable although temperature and pressure were easily read. RH readings on also unstable for one sensor using the 
Adafruit library so that sensor might have other issues. I am still have trouble with one of my sensors.  The ESP32C3 dev kit modules might be too fast for no hold readings. 

If you download the monitoring program you should replace the sensor characteristic UUIDs and the device service UUID with your own UUIDS.   You will also need to modify the
server to post your desired name for your BLE device.  I verified each BLE address using the Nrf app on my cell phone to connect to the device and then read the characteristic values.  
That app is also useful to check the device signal strength.  

My ESP32C3 did not use the default I2C lines that the  MS8607 library expected.  By addoing Wire.begin(SDA,SCL) to  the setup section or the program I was able to overide the default values.  I set the pins for my devices before the program starts the MS8607.   The BME code examples have already built in an option to select different I2C pins so this step should not be necessary with that sensor.  If wire has already begun apparently the MS 8607 library does not try to modify.   Another issue was that when both sensors used the same pins I appeared to get a conflict.  I used pins 5,6 for one device and 2,3 for the other and this seemed to fix that issue.

Msny thanks are due to Arduino, ESPressif, Stackoverflow, and all of the python code teams available via google.

Waszee
