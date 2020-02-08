/*
  Fade

  This example shows how to fade an LED on pin 9 using the analogWrite()
  function.

  The analogWrite() function uses PWM, so if you want to change the pin you're
  using, be sure to use another PWM capable pin. On most Arduino, the PWM pins
  are identified with a "~" sign, like ~3, ~5, ~6, ~9, ~10 and ~11.

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/Fade
*/

int led = 9;           // the PWM pin the LED is attached to
int adc = A0;
int brightness = 0;    // how bright the LED is
int fadeAmount = 5;    // how many points to fade the LED by
float led_v = 0.000;
int num_samples = 250;
float bit_depth = 1023.000;
int vcc = 5;

// the setup routine runs once when you press reset:
void setup() {
  // declare pin 9 to be an output:
  Serial.begin(115200);
  pinMode(led, OUTPUT);
  pinMode(adc, INPUT);
}

// the loop routine runs over and over again forever:
void loop() {
  // set the brightness of pin 9:
  analogWrite(led, brightness);

  // change the brightness for next time through the loop:
  brightness = brightness + fadeAmount;

  // reverse the direction of the fading at the ends of the fade:
  if (brightness <= 0 || brightness >= 255) {
    fadeAmount = -fadeAmount;
    brightness = brightness + fadeAmount;
  }

  long sum = 0;
  for (int i = 0; i < num_samples; i++) {
    sum += analogRead(adc);
  }
  led_v = vcc - (vcc * sum / num_samples / bit_depth * 2);

  // wait for 30 milliseconds to see the dimming effect
  Serial.print("Brightness: ");
  Serial.print(brightness / 255.0);
  Serial.print(" Voltage: ");
  Serial.println(led_v);
}
