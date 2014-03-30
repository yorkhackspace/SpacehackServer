//mxDNA March 2014 - display a DNA strand animation on a MAX7219
//8x8 LED matrix display
#include "LedControl.h"
#define INCREMENT 0.3  //how much to increment sine wave
#define GAP 1          //gap between DNA pairs
#define DELAY 50       //animation delay between steps
#define SHOWDNA true   //if false, just shows sine wave instead

//pins to MAX7219
int pinData=7;
int pinLoad=5;
int pinClock=6;
byte ledBuffer[8]; //main text window
//The MAX7219 LED Controller chip
LedControl lc = LedControl(pinData, pinClock, pinLoad, 1);
float x;
int c;

void setup() {
  // put your setup code here, to run once:
  /*
   The MAX72XX is in power-saving mode on startup,
   we have to do a wakeup call
   */
  lc.shutdown(0,false);
  /* Set the brightness to a medium values */
  lc.setIntensity(0,15);
  /* and clear the display */
  lc.clearDisplay(0);
  x = 0.0;
  c=0;
}

void loop() {
  // put your main code here, to run repeatedly: 
  for (int i = 7; i>0; i--) {
    ledBuffer[i] = ledBuffer[i-1];
  }
  int pos = (sin(x) + 1.0)/2.0 * 8.0;
  ledBuffer[0] = 1 << pos;
  
  if (SHOWDNA) {
    int pos2 = (cos(x+0.6) + 1.0)/2.0 * 8.0;
    ledBuffer[0] |= 1 << pos2;
    
    if (c++ == GAP) {
      if (pos2 > pos) {
        for (int i = pos; i < pos2; i++) {
          ledBuffer[0] |= 1 << i;
        }
      } else {
        for (int i = pos2; i < pos; i++) {
          ledBuffer[0] |= 1 << i;
        }
      }
      c = 0;
    }
  }
  
  for (int i = 0; i<=8; i++) {
    lc.setRow(0, i, ledBuffer[i]);
  }
  x+= INCREMENT;
  delay(DELAY);
}
