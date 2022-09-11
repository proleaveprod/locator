#include "locator_lib.h"

LiquidCrystal_I2C lcd(0x27,16,2);
Servo   servo;
VL53L0X laser;

void Locator::modeSet(){      //  Выбор режима работы устройства
  while(1){
    uartParse();          // Парсинг-прием строки с параметрами $maxV minV expK;
    if(curMode)break;  // Если что-то появилось - выходим из парсинга
  }
  tone(beeperPin,1046,100);
  delay(10);
  
  if(curMode==1)StartMode1();
  else if(curMode==2)StartMode2();
  else if(curMode==3)StartMode3();
}

void Locator::StartMode1(){   //  Запуск режима "Локатор"  
  lcd.clear();
  lcd.print("     MODE 1");
  lcd.setCursor(0,1);
  lcd.print("    LOCATOR");
  
  while(1){
    for(curAngle=minAngle-1;curAngle<maxAngle;curAngle+=dAngle){
      servoWrite(curAngle);
      delay(UART_INTERVAL);
      curRange=laser_read();
      String r = String(curRange);
      String fi = String(curAngle);
      String message= 'r'+r+'f'+fi+';';
      Serial.println(message);
      stopCheck();      
    }
    for(curAngle=maxAngle;curAngle>minAngle-1;curAngle-=dAngle){
      servoWrite(curAngle);
      delay(UART_INTERVAL);
      curRange=laser_read();
      String r = String(curRange);
      String fi = String(curAngle);
      String message= 'r'+r+'f'+fi;
      message+=';';
      Serial.println(message);
      stopCheck();
    }
  } 
}

void Locator::StartMode2(){   //  Запуск режима одиночных измерений 
  servoWrite(curAngle);
  delay(300);
  curRange=laser_read();
  Serial.println(curRange);
  lcd.clear();
  lcd.print("fi = ");
  lcd.print(curAngle);
  lcd.print(" ");
  lcd.print((char)223);
  lcd.setCursor(0,1);
  lcd.print("R = ");
  lcd.print(curRange);
  lcd.print(" mm");
  
  curMode=0;
  modeSet();
  
}
void Locator::StartMode3(){   //  Запуск режима измерения радиальной скорости по дифф. R
  servoWrite(curAngle);
  delay(300);
  curRange=laser_read();
  lcd.clear();
  lcd.print("     MODE 3   ");
  lcd.setCursor(0,1);
  lcd.print(" SPEED MEASURE");
  while(1){
    speed_read();
    stopCheck();
  }
}

void Locator::uartParse(){    //  Функция получения с компьютера настроек локатора
  while (Serial.available() > 0) {
    char incomingByte = Serial.read();      // обязательно ЧИТАЕМ входящий символ

    if (incomingByte == '$') {              // если это $
      getStarted = true;                    // поднимаем флаг, что можно парсить
    } else if (incomingByte != ';' && getStarted) { // пока это не ;
      // в общем происходит всякая магия, парсинг осуществляется функцией strtok_r
      inputData[index] = incomingByte;
      index++;
      inputData[index] = NULL;
    } else {
      if (getStarted) {
        char *p = inputData;
        char *str;
        index = 0;
        String value = "";
        while ((str = strtok_r(p, " ", & p)) != NULL) {
          string_convert = str;
          intData[index] = string_convert.toInt();
          index++;
        }
        index = 0;
      }
    }
    if (incomingByte == ';') {        // если таки приняли ; - конец парсинга
      getStarted = false;
      recievedFlag = true;
      Serial.print("LOCATOR+SET+OK");    // Специальное сообщение для компьютера об успешном парсинге параметров
      delay(300);

      curMode =intData[0];
      if(curMode==1){
        minAngle=intData[1];              //запись их в переменные
        maxAngle=intData[2];
        dAngle=intData[3];
      }else if(curMode==2||curMode==3){
        curAngle=intData[1];
      }

 
    }
  }
}

void Locator::uart_send(int data_to_send){     // Отправка числа по uart (защита от переполнения буффера)
  if(millis()-lastTime2 > UART_INTERVAL){  // Алгоритм, нужный для того, чтобы можно было вызывать Serial.println(...) раз в UART_INTERVAL миллисекунд.
          lastTime2=millis();      
          Serial.println(data_to_send);    // Отправка числа по uart на компьютер
  }
}

void Locator::stopCheck(){    //  Стоп-символ для выхода из непрерывных измерений
  if(Serial.available()){
        byte a = Serial.read();
        if(a=='s'){
          curMode=0;
          lcd.clear();
          lcd.print("      STOP      ");
          delay(1000);
          lcd.clear();
          modeSet();
        }
      }
}

void Locator::welcome(){    //  Функция приветствия пользователя (звук, serial, экран)
  Serial.print("LOCATOR+OK");
  lcd.print("LOCATOR IS READY");
  tone(beeperPin,523,100);
  delay(100);
  tone(beeperPin,784,100);
  delay(100);
  tone(beeperPin,1046,100);
  delay(100); 
  delay(1100);
  lcd.clear(); 

}


void Locator::servoWrite(int ugol){ //  Реверс-функция для серво-привода (можно было просто прочитать по-внимательнее мануал по либе servo :) )
  ugol = -ugol;
  ugol += 180;
  servo.write(ugol);
}

void Locator::pin_init(){   //  Инициализация всех GPIO-портов + servo + lcd 
  pinMode(beeperPin,OUTPUT);
  servo.attach(servoPin);
  servo.write(90);
  
  lcd.init();
  lcd.backlight();
}

void Locator::laser_init(){ //  Инициализация и настройка ToF-датчика VL53L0X
  Wire.begin();        // Включение I2C шины
  laser.setTimeout(500);  // Выставление времени ожидания отклика модуля в мс.
  #if defined LONG_RANGE  
    laser.setSignalRateLimit(0.1); // понижает предел скорости обратного сигнала (по умолчанию 0,25 MCPS (мчип/с))
    // увеличить периоды лазерного импульса (по умолчанию 14 и 10 PCLK)
    // * - PCLK — это частота периферии
    laser.setVcselPulsePeriod(VL53L0X::VcselPeriodPreRange, 18);
    laser.setVcselPulsePeriod(VL53L0X::VcselPeriodFinalRange, 14);
  #endif
  #if defined HIGH_ACCURACY
    // увеличить тайминг 200 мс
    laser.setMeasurementTimingBudget(200000);
  #endif
//________________________________________________________________________________________________________________
  if (!laser.init())
    {
      Serial.println("VL53L0X+ERROR");  // В случае, если дальномер не откликнулся за время ожидания, программа зависает
      lcd.print("VL53L1X ERROR");
 
      while(1);
    } 
      //Serial.println("#SONAR_READY");  // В случае успешной инициализации, по UART выдается сообщение о готовности модуля.
}

void Locator::math_mode(){   // Режим для получения большой выборки для исследования статистических характеристик датчика.
  Serial.println();
  for (int i = 0; i < 1000; i++) { // i от 0 до 16
  Serial.print(i);      // номер замера
  Serial.print("\t");   // табуляция
  Serial.println(laser_read());
  tone(beeperPin,1000,5);
  }
}
void Locator::speed_read(){  // Функция режима измерителя скорости. Вычисление производится через производную от расстояния.
  t1 = micros();     
  s1=laser_read();
  if(s1>MAX_RANGE)s1 = lastRange;
  lastRange = s1;
  s1=s1*1000;          // При умножении на 1 - м/с ; на 10 - см/c ; на 100 - мм/с
  dt = micros()-t1;       
  float _speed = (s2-s1);
  _speed= _speed/dt;
  
  String sign = "0 ";  
  if(_speed>0)sign="0 ";
  else sign="1 ";
  long a = long(_speed*1000);
  String message = sign + String(a);
  Serial.print(message);
  s2 = s1;
}

long Locator::laser_read(){    // Функция считывания расстояния
  long a = laser.readRangeSingleMillimeters();  
  Serial.print("L:r= ");
  Serial.println(a); 
  return a;
}
