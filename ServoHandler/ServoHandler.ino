#include <ESP32Servo.h>

Servo handler;

const int servo = 13, red = 25, green = 26;

void setup() {
  // put your setup code here, to run once:
  // Allow allocation of all timers
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  handler.setPeriodHertz(50);    // standard 50 hz servo
  handler.attach(servo, 544, 2400);
  Serial.begin(9600);
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  digitalWrite(red, LOW);
  digitalWrite(green, LOW);
}

void loop() {
  Serial.println("Waiting...");
  while(!Serial.available()); //wait until data received
  Serial.print("Data received: ");
  char led = Serial.read();
  if(led == 'r')
  {
    digitalWrite(red, HIGH);
    digitalWrite(green, LOW);
    Serial.print("RED");
  }
  else if(led == 'g')
  {
    digitalWrite(red, LOW);
    digitalWrite(green, HIGH);
    Serial.print("GREEN");
  }
  else
  {
    digitalWrite(red, LOW);
    digitalWrite(green, LOW);
    Serial.print("OFF");
  }
  int servo_angle = Serial.parseInt();
  Serial.print("|");
  handler.write(servo_angle);
  Serial.println(servo_angle);
}
