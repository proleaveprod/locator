#include "locator_lib.h"

#define  SERVO_PIN     11       
#define  BEEPER_PIN   10

#define HIGH_ACCURACY   // При раскомментировании датчик настраивается под высокую точность считывания значений
//#define LONG_RANGE    // При раскомментировании датчик настраивается под высокую даьность измерений.

Locator locator(SERVO_PIN,BEEPER_PIN);

void setup() {               
  Serial.begin(9600);         
  pinMode(10,OUTPUT);
  
  locator.pin_init();
  locator.laser_init();
  locator.welcome();

  locator.modeSet();
  //locator.math_mode();
}

void loop() {             

}
