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
int adc = A0;          // Reading in LED Voltage / 2
int brightness = 255;    // how bright the LED is

float led_v = 0.000;   // Voltage on the LED
float target = 0.000;  // Target LED voltage
int num_samples = 250; // Number of averages
float bit_depth = 1023.000;
float fudge = 0.05;

int vcc = 5;
String buff = String("deadbuffdead");
long sum = 0;
uint8_t fudge_judge;

// the setup routine runs once when you press reset:
void setup() {
  // declare pin 9 to be an output:
  Serial.begin(115200);
  pinMode(led, OUTPUT);
  pinMode(adc, INPUT);
}

uint8_t fudge_zone() {
  if (target > (led_v + fudge)) {
    return 0;
  } else if (target < (led_v - fudge)) {
    return 1;
  } else {
    return 2;
  }
}

// the loop routine runs over and over again forever:
void loop() {
  sum = 0;
  for (int i = 0; i < num_samples; i++) {
    sum += analogRead(adc);
  }
  led_v = vcc - (vcc * sum / num_samples / bit_depth * 2);

  fudge_judge = fudge_zone();

  if (fudge_judge == 2) {
    ;
  } else if (fudge_judge == 1 && brightness < 255) {
    brightness += 1;
  } else if (fudge_judge == 0 && brightness > 0) {
    brightness -= 1;
  }

  analogWrite(led, brightness);

  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');
//    Serial.println(buff);
    target = buff.toFloat();
    Serial.print("\nFudge: ");
    Serial.println(fudge_judge);
    Serial.print("Brightness: ");
    Serial.println(brightness);
    Serial.print("Voltage: ");
    Serial.println(led_v);
    Serial.print("Target: ");
    Serial.println(target);
  }

  delay(1);
}
