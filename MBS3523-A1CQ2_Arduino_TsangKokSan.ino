#include <Servo.h> 

Servo left_right;  // Declare a servo object for controlling left-right movement
Servo up_down;     // Declare a servo object for controlling up-down movement

void setup() { 
  left_right.attach(9);  // Attach the left-right servo to pin 9
  up_down.attach(10);    // Attach the up-down servo to pin 10
  Serial.begin(115200);  // Initialize serial communication at 115200 baud
} 

void loop() { 
  while(Serial.available()) { // Check if there is data available to read from serial port
    String inputString = Serial.readStringUntil('\r');  // Read the incoming data until '\r' (carriage return) is encountered
    
    int commaIndex = inputString.indexOf(',');  // Find the index of the comma in the string
    
    if (commaIndex != -1) {  // If a comma is found in the string
      int x_axis = inputString.substring(0, commaIndex).toInt();  // Extract the x-axis value before the comma and convert it to an integer
      int y_axis = inputString.substring(commaIndex + 1).toInt();  // Extract the y-axis value after the comma and convert it to an integer

      int y = map(y_axis, 0, 1080, 180, 0);  // Map the y-axis value from the range 0-1080 to the range 180-0
      int x = map(x_axis, 0, 1920, 180, 0);  // Map the x-axis value from the range 0-1920 to the range 180-0

      left_right.write(x);  // Set the position of the left-right servo based on the mapped x-axis value
      up_down.write(y);     // Set the position of the up-down servo based on the mapped y-axis value

      Serial.print("First Integer: ");  // Print the label for the first integer
      Serial.println(x);  // Print the mapped x-axis value
      Serial.print("Second Integer: ");  // Print the label for the second integer
      Serial.println(y);  // Print the mapped y-axis value
    } 
  } 
}