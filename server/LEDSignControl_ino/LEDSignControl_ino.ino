/*
 * IRremote: IRrecvDump - dump details of IR codes with IRrecv
 * An IR detector/demodulator must be connected to the input RECV_PIN.
 * Version 0.1 July, 2009
 * Copyright 2009 Ken Shirriff
 * http://arcfn.com
 * JVC and Panasonic protocol added by Kristian Lauszus (Thanks to zenwheel and other people at the original blog post)
 */

#include <IRremote.h>
#include <Wire.h>

#define LED_REMOTE_ON 0xF7C03F
#define LED_REMOTE_OFF 0xF740BF
#define LED_REMOTE_UP 0xF700FF
#define LED_REMOTE_DOWN 0xF7807F
#define LED_REMOTE_FLASH 0xF7D02F
#define LED_REMOTE_STROBE 0xF7F00F
#define LED_REMOTE_FADE 0xF7C837
#define LED_REMOTE_SMOOTH 0xF7E817

#define LED_REMOTE_WHITE 0xF7E01F
#define LED_REMOTE_RED 0xF720DF
#define LED_REMOTE_GREEN 0xF7A05F
#define LED_REMOTE_BLUE 0xF7609F

#define LED_REMOTE_YELLOW 0xF728D7
#define LED_REMOTE_CYAN 0xF7B04F
#define LED_REMOTE_MAGENTA 0xF76897

#define LED_REMOTE_RED_1 0xF710EF
#define LED_REMOTE_RED_2 0xF730CF
#define LED_REMOTE_RED_3 0xF708F7
#define LED_REMOTE_RED_4 0xF728D7
#define LED_REMOTE_GREEN_1 0xF7906F
#define LED_REMOTE_GREEN_2 0xF7B04F
#define LED_REMOTE_GREEN_3 0xF78877
#define LED_REMOTE_GREEN_4 0xF7A857
#define LED_REMOTE_BLUE_1 0xF750AF
#define LED_REMOTE_BLUE_2 0xF7708F
#define LED_REMOTE_BLUE_3 0xF748B7
#define LED_REMOTE_BLUE_4 0xF76897

#define MODE_OFF 0
#define MODE_SOLID 1
#define MODE_FLASH 2
int mode = MODE_OFF;
int code1 = LED_REMOTE_RED;
int code2 = LED_REMOTE_RED_1;
unsigned long flashDelay = 300;


//int RECV_PIN = 11;

//IRrecv irrecv(RECV_PIN);

IRsend irsend;

//decode_results results;

int getCode(char input){
  switch (input){
    case '!': return LED_REMOTE_ON;
    case ')': return LED_REMOTE_OFF;
    case '^': return LED_REMOTE_UP;
    case 'v': return LED_REMOTE_DOWN;
    case '*': return LED_REMOTE_FLASH;
    case '%': return LED_REMOTE_STROBE;
    case '\\': return LED_REMOTE_FADE;
    case '~': return LED_REMOTE_SMOOTH;
    case 'w': return LED_REMOTE_WHITE;
    case 'r': return LED_REMOTE_RED;
    case 'g': return LED_REMOTE_GREEN;
    case 'b': return LED_REMOTE_BLUE;
    case 'y': return LED_REMOTE_YELLOW;
    case 'c': return LED_REMOTE_CYAN;
    case 'm': return LED_REMOTE_MAGENTA;
    case 'i': return LED_REMOTE_RED_1;
    case 'o': return LED_REMOTE_RED_2;
    case 'p': return LED_REMOTE_RED_3;
    case 'j': return LED_REMOTE_GREEN_1;
    case 'k': return LED_REMOTE_GREEN_3;
    case 'l': return LED_REMOTE_GREEN_4;
    case 'a': return LED_REMOTE_BLUE_1;
    case 's': return LED_REMOTE_BLUE_2;
    case 'd': return LED_REMOTE_BLUE_3;
  }
  return LED_REMOTE_OFF;
}

void setup()
{
  Serial.begin(9600);
  Wire.begin(4);                // join i2c bus with address #4
  //Wire.onReceive(receiveEvent); // register event
  //irrecv.enableIRIn(); // Start the receiver
  //pinMode(9, OUTPUT);
  //digitalWrite(9, LOW);
  
  //pinMode(10, OUTPUT);
  //digitalWrite(10, HIGH);
  
}

/*
void dump(decode_results *results) {
  if (results->decode_type == NEC) {
    Serial.print("Decoded NEC: ");
    Serial.println(results->value, HEX);
    switch(results->value){
      case LED_REMOTE_ON: Serial.println("On"); break;
case LED_REMOTE_OFF: Serial.println("Off"); break;
case LED_REMOTE_UP: Serial.println("Up"); break;
case LED_REMOTE_DOWN: Serial.println("Down"); break;
case LED_REMOTE_FLASH: Serial.println("Flash"); break;
case LED_REMOTE_STROBE: Serial.println("Strobe"); break;
case LED_REMOTE_FADE: Serial.println("Fade"); break;
case LED_REMOTE_SMOOTH: Serial.println("Smooth"); break;
case LED_REMOTE_WHITE: Serial.println("White"); break;
case LED_REMOTE_RED: Serial.println("Red"); break;
case LED_REMOTE_GREEN: Serial.println("Green"); break;
case LED_REMOTE_BLUE: Serial.println("Blue"); break;
case LED_REMOTE_YELLOW: Serial.println("Yellow"); break;
case LED_REMOTE_CYAN: Serial.println("Cyan"); break;
case LED_REMOTE_MAGENTA: Serial.println("Magenta"); break;
case LED_REMOTE_RED_1: Serial.println("Red 1"); break;
case LED_REMOTE_RED_2: Serial.println("Red 2"); break;
case LED_REMOTE_RED_3: Serial.println("Red 3"); break;
case LED_REMOTE_GREEN_1: Serial.println("Green 1"); break;
case LED_REMOTE_GREEN_3: Serial.println("Green 3"); break;
case LED_REMOTE_GREEN_4: Serial.println("Green 4"); break;
case LED_REMOTE_BLUE_1: Serial.println("Blue 1"); break;
case LED_REMOTE_BLUE_2: Serial.println("Blue 2"); break;
case LED_REMOTE_BLUE_3: Serial.println("Blue 3"); break;
default: Serial.println("Error"); break;
    }
  }
}
*/

unsigned long lastTime = 0;
unsigned long lastFlash = 0;
boolean flashvar = false;

boolean hasNext(int source){
  switch (source){
    case 1: //serial
      return Serial.available();
    break;
    case 2: //i2c
        return Wire.available();
    break;
  }
}

char getNext(int source){
  switch (source){
    case 1: //serial
      return Serial.read();
    break;
    case 2: //i2c
      char in = Wire.read();
      Serial.print(in);
      return in;
    break;
  }  
}

void parseInput(char in, int source){
  delay(20);
  
    Serial.println("Got input");
    switch (in){
      case 'M':
        Serial.println("Got mode");
        //mode
        if (hasNext(source)){
          char in2 = getNext(source);
          switch (in2){
            case 'f': mode = MODE_FLASH; break;
            case 's': mode = MODE_SOLID; break;
            case 'o': mode = MODE_OFF; break;
          }
        }
        break;
      case '1': 
        Serial.println("Got code 1");
        //Select Code 1
        if (hasNext(source)){
          code1 = getCode(getNext(source));
        }
        break;
      case '2':
        Serial.println("Got code 2");
        //Select code 2
        if (hasNext(source)){
          code2 = getCode(getNext(source));
        }
        break;
      case 'F':
        Serial.println("Got freq");      
        //Frequency - Next byte is a number between 0 and 255. This represents a period from 20 to 1040 mS.
        if (hasNext(source)){
          flashDelay = map(getNext(source), 0, 255, 20, 20+255*4);
        }
        break;
    }
}

void loop() {
  //if (irrecv.decode(&results)) {
  //  dump(&results);
  //  irrecv.resume(); // Receive the next value
  //}
  
  if (millis()-1000>lastTime){ //every second
    lastTime = millis();
    switch(mode){
      case MODE_OFF: irsend.sendNEC(LED_REMOTE_OFF, 32); break;
      case MODE_SOLID: irsend.sendNEC(LED_REMOTE_ON, 32); irsend.sendNEC(code1, 32); break;
      case MODE_FLASH: irsend.sendNEC(LED_REMOTE_ON, 32); break;      
    }
  }
  
  if (mode == MODE_FLASH){
    if (millis()-flashDelay>lastFlash){ //every second
      lastFlash = millis();
      if (flashvar){
        irsend.sendNEC(code1, 32);
      }
      else{
        irsend.sendNEC(code2, 32);
      }
      flashvar = !flashvar;
    }
  }
  
  if (hasNext(1)){
    parseInput(getNext(1), 1);
  }
  if (hasNext(2)){
    parseInput(getNext(2), 2);
  }
}

//example codes
/*

Ms1g - Solid green
Mf1r2iF\ - Approx 1Hz red and yellow flash

*/
