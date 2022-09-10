#ifndef LOCATOR_LIB_H
#define LOCATOR_LIB_H

#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <VL53L0X.h>
#include <LiquidCrystal_I2C.h>






#define UART_INTERVAL   15    //  Интервал между сообщениями, которые передаются компьютеру через UART шину (мс)
#define PARSE_AMOUNT    4      //  Число значений в массиве, которые хотим получить из пакета с настройками 4 шт (режим, параметр1, параметр2, параметр3)
#define INPUT_AMOUNT    20     //  Максимальное количество символов в пакете, который идёт в сериал 
#define MAX_RANGE       1000 






class Locator{
  
  public:
  Locator(uint8_t serPin,uint8_t beepPin){
      servoPin  =  serPin;
      beeperPin =  beepPin; 
        
  }
  void modeSet();
  void StartMode1();
  void StartMode2();
  void StartMode3();
  
  void welcome();
  void pin_init();
  void laser_init();
  void math_mode();
  
  
  uint8_t curMode;   //  Текущий режим работы устройства

  uint32_t lastTime1; //  Переменные для реализации таймеров запуска функций.  
  uint32_t lastTime2; //  lastTime1 (мкс) для интегрирования по периоду,    lastTime2 (мс) для отправки по uart сообщений
  
  uint32_t curRange;  // расстояние в мм.
  uint32_t lastRange;                             
                                
  uint8_t maxAngle,minAngle,curAngle,dAngle;

  private:

    void uartParse();
    void uart_send(int data_to_send);
    void stopCheck();

    void servoWrite(int ugol);

    void speed_read();
    long laser_read();

    char inputData[INPUT_AMOUNT];  //   Массив входных значений (СИМВОЛЫ)
    int intData[PARSE_AMOUNT];     //   Массив численных значений после парсинга
    String string_convert;         // Нужно, чтобы вытащить из сообщения int
    boolean recievedFlag;
    boolean getStarted;
    byte index;

    long t1,dt;     // Дифференциирование расстояния(нахождение скорости)
    float s1,s2;

    uint8_t servoPin;
    uint8_t beeperPin;


  
};




















#endif //LOCATOR_LIB_H
