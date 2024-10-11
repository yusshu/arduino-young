// Copyright (c) Andre Roldan
// Licensed under the MIT license

// This program just waits until it reads a number 't' from the
// serial port, then reads 't' distances using the HC-SR04 sensor
// and writes them back to the serial port

// Factor for converting microseconds (time for the signal to
// go and come back) to milimeters (calculated distance)
// 
// It's the sound speed in the air at 20°C (343m/s) in milimeters
// per microsecond, over two
#define CONVERSION 0.1715

// HC-SR04 pins
// Trigger pin  ->  D6
// Echo pin     ->  D7
const uint8_t trigPin = 6;
const uint8_t echoPin = 7;

int remainingReads = 0;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  if (remainingReads > 0) {
    // 10us pulse (check https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    // Read echo
    long distance = (pulseIn(echoPin, HIGH) * CONVERSION);
    if (distance > 0) {
      Serial.println(distance);
      remainingReads--;
    }
  } else if (Serial.available() > 0) {
    // Wait for input
    remainingReads = Serial.readStringUntil('\n').toInt();
  }
  delay(10);
}
