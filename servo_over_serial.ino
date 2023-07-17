
# include <Servo.h>

// Intializing servo objects
Servo xServo; 
Servo yServo;

void setup() {
  Serial.begin(9600);
  // Give each servo a PWM pin
  xServo.attach(3); yServo.attach(5);
  // Set start position for each servo
  xServo.write(90); yServo.write(10);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  static String msg = "";
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '.') {
      // End of message, parse target point
      int xPos, yPos;
      sscanf(msg.c_str(), "%d,%d", &xPos, &yPos);
      // Move servos to target position
      xPos = constrain(xPos, 10, 170);
      yPos = constrain(yPos, 10, 170);
      xServo.write(xPos);
      yServo.write(yPos);
      msg = "";
    } else {
      // Add character to message
      msg += c;
    }
  }
}