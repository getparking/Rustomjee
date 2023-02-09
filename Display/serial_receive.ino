#include <Arial14.h>
#include <Arial_Black_16_ISO_8859_1.h>
#include <Arial_black_16.h>
#include <DMD.h>
#include <SPI.h>
#include <TimerOne.h>

String str;
String ctr;
char b[8];
char x[8];
DMD dmd(1, 1);
size_t
mymsg;
char Mymessage[4];
char tmp[4];

void ScanDMD() {
  dmd.scanDisplayBySPI();
}

void setup() {
  Serial.begin(9600);
  Timer1.initialize(5000);
  Timer1.attachInterrupt(ScanDMD);
  dmd.clearScreen(true);
}

void loop() 
{
  mymsg = Serial.readBytesUntil(' ', Mymessage, 3);
  String mystring = Mymessage;
  dmd.clearScreen(true);
  dmd.selectFont(Arial_Black_16);
  int slen = 0;
  str = mystring;
  slen = str.length() + 1;
  str.toCharArray(b, slen);
  dmd.drawString(2, 1, b, slen, GRAPHICS_NORMAL);
  delay( 100 );
  mystring = "";
}
