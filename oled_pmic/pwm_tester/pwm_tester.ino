int led = 9;           // the PWM pin the LED is attached to
int adc = A0;          // Reading in LED Voltage / 2
int brightness = 255;    // how bright the LED is

float led_v = 0.000;
float target = 0.000;  // Target LED voltage
int num_samples = 250; // Number of averages
float bit_depth = 1023.000;

int vcc = 9;
String buff = "";

float pwm_voltages[256];
unsigned long elapsed;

// the setup routine runs once when you press reset:
void setup() {
  // declare pin 9 to be an output:
  Serial.begin(115200);
  buff.reserve(200);
  pinMode(led, OUTPUT);
  pinMode(adc, INPUT);
  analogWrite(led, 0);
  calibrate_led();
  elapsed = millis();
}

void calibrate_led() {
  Serial.print("\nCalibrating");
  for (int i = 0; i < 256; i++) {
    analogWrite(led, i);
    delay(0.5);
    pwm_voltages[i] = read_voltage();
    if (i % 10 == 0) {
//      Serial.print(i);
//      Serial.print(" = ");
//      Serial.println(pwm_voltages[i]);
      Serial.print(".");
    }
  }
  Serial.println("\nCalibration Complete.");
}

float read_voltage() {
  float sum = 0;
  for (int i = 0; i < num_samples; i++) {
    sum += analogRead(adc);
  }
  return (vcc - (vcc * sum / num_samples / bit_depth * 2));
}

void write_voltage(float t) {
  target = t;
  if (target < pwm_voltages[255]) {
    brightness = 255;
  } else if (target > pwm_voltages[0]) {
    brightness = 0;
  } else {
    for (int i = 0; i < 256; i++) {
      if (pwm_voltages[i] < target) {
        brightness = i;
        break;
      }
    }
  }
  analogWrite(led, brightness);
  delay(1);
  led_v = read_voltage();
}

void serialEvent() {
  buff = Serial.readStringUntil('\n');
  //  Serial.print("SERIAL EVENT: ");
  //  Serial.println(buff);
  if (buff.compareTo("c") == 0) {
    calibrate_led();
  } else if (buff.toFloat() != 0) {
    write_voltage(buff.toFloat());
    Serial.print("\nDuty Cycle (8 bit): ");
    Serial.println(brightness);
    Serial.print("Voltage (V): ");
    Serial.println(led_v);
    Serial.print("Target  (V): ");
    Serial.println(target);
  }
}
void loop() {
  delay(10);
}
