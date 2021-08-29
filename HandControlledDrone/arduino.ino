/*
  Code Created by: Ish Kadakia
  Date Last Updated:

  This arduino recieves a 6-char string from the serial port, and 
  outputs to pins on the arduino.
  

  The analogWrite of certain pins indicates the power of the throttle
  or rotation, and should connect to an infrared controller of a 3 channel
  helicopter. 
*/

// Servo beacuase i dont have enough LEDS
#include <Servo.h>
Servo myServo; 

// Pins controlling UP/DOWN
int vx0pos = 2;   //UP
int vx0neg = 3;   //DOWN

// Pins controlling CW/CCW
int vy0pos = 5;   //CW
int vy0neg = 6;   //CCW

// Pins controlling FORWARD/BACKWARDS
int forw   = 8;   //FORWARD
int back   = 9;   //BACK

String str = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

void setup() {
  // initialize serial:
  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  str.reserve(200);

  // Set pinmodes
  pinMode(vx0pos, OUTPUT);
  pinMode(vx0neg, OUTPUT);
  pinMode(vy0pos, OUTPUT);
  pinMode(vy0neg, OUTPUT);
  pinMode(forw, OUTPUT);
  pinMode(back, OUTPUT);

  // Set Servo
  myServo.attach(14);

}

void loop() {
  // print the string when a newline arrives:
  while (!Serial.available()) {} // Do nothing
  
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the input string 'str':
    str += inChar;
    // if the incoming character is a newline
    // set a flag to end reading the string
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
  if (stringComplete) {
    // Uncomment to see the input on the serial monitor
    //Serial.print(str);

    // Sending the info to the arduino's pins

    if (str[0] == '0') { // CW Direction
      analogWrite(vx0pos, (str[1]-'0')*28);   
      analogWrite(vx0neg, 0);
    } else if (str[0] == '1') {  // CCW Direction
      analogWrite(vx0neg, (str[1]-'0')*28);
      analogWrite(vx0pos, 0);
    }
    
    if (str[2] == '0') {  // UP direction
      analogWrite(vy0pos, int(str[3]-'0')*28);
      analogWrite(vy0neg, 0);
    } else if (str[0] == '1') { // DOWN direction
      analogWrite(vy0pos, 0);
      analogWrite(vy0neg, int(str[3]-'0')*28);
    }

    // This was just a servo to test whether the inputs were working
    // Due to lack of equipment the servo was the only thing i had left
    if (str[4] == '1') {
      myServo.write(90);
    } else {
      myServo.write(180);
    }

/*  When I get more LEDS to test the activation of 
    if (str[4] == '1') {  // Forward
      digitalWrite(forw, HIGH);
    } else {
      digitalWrite(forw, LOW);
    }
    if (str[5] == '1') {  // Backwards
      digitalWrite(back, HIGH);
    } else{
      digitalWrite(back, LOW);
    }
*/
  // clear the string:
  str = "";
  stringComplete = false;
  }
}
