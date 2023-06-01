/*********
  Rui Santos
  Complete instructions at https://RandomNerdTutorials.com/esp32-ble-server-client/
  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files.
  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

   Code modified by waszee to change from BME type sensor to anTE MS8607 PTH sensord using the Adadruit libraries for MS8607
   Note the i2c pins for the ESP32-C#-DevKit-1U requres Wire.begin(5.6) line.    


*********/

#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Wire.h>
#include <Adafruit_MS8607.h>
#include <Adafruit_Sensor.h>

Adafruit_MS8607 ms8607;

//BLE server name
#define bleServerName "THP_BLE_ESP32SC3_2nda"
// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID "4cd0c3b5-ace1-46c8-92bc-ec930cc210ae"
#define UUID1 "5eaac482-b210-4216-a269-aa20c74856b6"
#define UUID2 "0c74216d-03be-4ccb-b29e-efc6d0ae8c54"
#define UUID3 "e0503252-db3a-4700-884a-97e7effc2ab9"

//define the ESP32 pins for the I2C SDA and CLK
#define SDA 2
#define CLK 3

double temp;
double tempF;
double hum;
double pressure;

// Timer variables
unsigned long lastTime = 0;
unsigned long timerDelay = 30000;


BLEServer* pServer = NULL;
//BLECharacteristic* pCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

// Temperature Characteristic and Descriptor
BLECharacteristic ms8607TemperatureCelsiusCharacteristic(UUID1, BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
BLEDescriptor ms8607TemperatureCelsiusDescriptor(BLEUUID((uint16_t)0x2902));

// Humidity Characteristic and Descriptor
BLECharacteristic ms8607HumidityCharacteristic(UUID2,BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
BLEDescriptor ms8607HumidityDescriptor(BLEUUID((uint16_t)0x2902));

// Pressure Characteristic and Descriptor
BLECharacteristic ms8607PressureCharacteristic(UUID3,BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY);
BLEDescriptor ms8607PressureDescriptor(BLEUUID((uint16_t)0x2902));


//Setup callbacks onConnect and onDisconnect
class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    deviceConnected = true;
  };
  void onDisconnect(BLEServer* pServer) {
    deviceConnected = false;
  }
};

void initms8607(){
  // Try to initialize!
  if (!ms8607.begin()){
    Serial.println("Failed to find MS8607 chip");
    while (1) { delay(10); }
  }
  Serial.println("MS8607 Found!\n\n\n"); 
}

void setup() {
  // Start serial communication 
  Serial.begin(115200);
  Wire.begin(SDA,CLK);  // sets esp32s3 to use pins 5 and 6 for sda and clk

  // Init ms8607 Sensor
  initms8607();

  // Create the BLE Device
  BLEDevice::init(bleServerName);

  // Create the BLE Server
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  // Create the BLE Service
  BLEService *ms8607Service = pServer->createService(SERVICE_UUID);

  // Create BLE Characteristics and Create a BLE Descriptor
  // Temperature

  ms8607Service->addCharacteristic(&ms8607TemperatureCelsiusCharacteristic);
  ms8607TemperatureCelsiusCharacteristic.setValue("Temperature Celsius");
  ms8607TemperatureCelsiusCharacteristic.addDescriptor(&ms8607TemperatureCelsiusDescriptor);
  
  // Humidity
  ms8607Service->addCharacteristic(&ms8607HumidityCharacteristic);
  ms8607HumidityCharacteristic.setValue("Humidity");
  ms8607HumidityCharacteristic.addDescriptor(&ms8607HumidityDescriptor);
 
  //Pressure
  ms8607Service->addCharacteristic(&ms8607PressureCharacteristic);
  ms8607PressureCharacteristic.setValue("Pressure");
  ms8607PressureCharacteristic.addDescriptor(&ms8607PressureDescriptor);
  
  // Start the service
  ms8607Service->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  //pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  //pAdvertising->setMaxPreferred(0x12);
  BLEDevice::startAdvertising();
  Serial.println("Waiting a client connection to notify...\n");
}

void loop() {
  
  // Notify if change to any characteristic of service and update the values of all characteristics
  if (deviceConnected) {
    //f ((millis() - lastTime) > timerDelay) {
      
    sensors_event_t tmp, pres, humid;
    Adafruit_Sensor *pressure_sensor = ms8607.getPressureSensor();
    Adafruit_Sensor *temp_sensor = ms8607.getTemperatureSensor();
    Adafruit_Sensor *humidity_sensor = ms8607.getHumiditySensor();

    // this is inefficient because it causes multiple reads of temperature and pressure, however it suffices to show how the interface works;
    temp_sensor->getEvent(&tmp);
    pressure_sensor->getEvent(&pres);
    humidity_sensor->getEvent(&humid);
      
      // Read temperature as Celsius (the default)
     
      temp = tmp.temperature;
      // Fahrenheit
      tempF = 1.8*temp +32;
      // Read humidity
      hum = humid.relative_humidity;
      pressure=pres.pressure + 13.25;  // adjusts sensor to approximate weather service sealevel values
  
      //Notify temperature reading from ms8607 sensor
      
      static char temperatureCTemp[8];
      dtostrf(temp, 8, 2, temperatureCTemp);
      //Set temperature Characteristic value and notify connected client
      ms8607TemperatureCelsiusCharacteristic.setValue(temperatureCTemp);
      ms8607TemperatureCelsiusCharacteristic.notify();
      Serial.print("Temperature Celsius: ");
      Serial.print(temp);
      Serial.print(" ºC\n");
      delay(500);
      //Notify humidity reading from ms8607
      static char humidityTemp[8];
      dtostrf(hum, 8, 2, humidityTemp);
      //Set humidity Characteristic value and notify connected client
      ms8607HumidityCharacteristic.setValue(humidityTemp);
      ms8607HumidityCharacteristic.notify();   
      Serial.print("Humidity: ");
      Serial.print(hum);
      Serial.println(" %");
      delay(500);

      //Notify pressure reading from ms8607
      static char pressureTemp[8];
      dtostrf(pressure, 6, 2, pressureTemp);
      //Set Pressure Characteristic value and notify connected client
      ms8607PressureCharacteristic.setValue(pressureTemp);
      ms8607PressureCharacteristic.notify();   
      Serial.print("Pressure: ");
      Serial.print(pressure);
      Serial.println(" hPa(mbars)\n");
      delay(5000);
      Serial.print("process time(ticks) = ");
      oldDeviceConnected=true;
      Serial.println(millis()-lastTime);
      lastTime = millis();
      
    //}
  }
  // disconnecting
  if (!deviceConnected && oldDeviceConnected) {
      delay(2000); // give the bluetooth stack the chance to get things ready
      pServer->startAdvertising(); // restart advertising
      Serial.println("start advertising");
      oldDeviceConnected = deviceConnected;
  }
  // connecting
  if (deviceConnected && !oldDeviceConnected) {
      // do stuff here on connecting
      oldDeviceConnected = false;
      Serial.println("In connecting Again");
      delay(3000);  
      Serial.println(deviceConnected);
      Serial.println(oldDeviceConnected);
  }

}