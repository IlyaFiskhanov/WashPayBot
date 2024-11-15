//module_settings.ino
#include "ESP_MICRO.h" //Include the micro library 

const int relayPin = D7;

void setup(){
  Serial.begin(9600); // Starting serial port for seeing details
  start("CrazyWifi","Qu5BTVpz");  // EnAIt will connect to your wifi with given details
  pinMode(relayPin, OUTPUT);
}
void loop(){
  waitUntilNewReq();  

  if (getPath()=="/OPEN_MACHINE"){
    digitalWrite(relayPin, HIGH);
  }
  if (getPath()=="/CLOSE_MACHINE"){
    digitalWrite(relayPin, LOW);
  }

}
