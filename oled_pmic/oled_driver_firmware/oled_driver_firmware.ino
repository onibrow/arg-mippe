const uint8_t leds[4] = {9, 6, 5, 3};           // the PWM pin the LED is attached to
const uint8_t adcs[4] = {A0, A1, A2, A3};          // Reading in LED Voltage / 2
const uint8_t num_samples = 250; // Number of averages
const int bit_depth = 1023;
const uint8_t vcc = 9;
const uint8_t cal_samples = 128;

uint8_t brightnesses[4] = {255, 255, 255, 255};    // how bright the LED is
int led_vs[4] = {0, 0, 0, 0};
float targets[4] = {0.000, 0.000, 0.000, 0.000};  // Target LED voltage
uint16_t pwm_voltages[4][cal_samples];

String buff = "";
unsigned long elapsed;

int test_led = 0;

// the setup routine runs once when you press reset:
void setup() {
  // declare pin 9 to be an output:
  Serial.begin(115200);
  buff.reserve(200);
  for (int led_num = 0; led_num < 4; led_num++) {
    pinMode(leds[led_num], OUTPUT);
    pinMode(adcs[led_num], INPUT);
    analogWrite(leds[led_num], 255);
  }
  calibrate_led();
  elapsed = millis();
}

void calibrate_led() {
  for (int led_num = 0; led_num < 4; led_num++) {
    Serial.print("\nCalibrating LED ");
    Serial.println(led_num);
    for (int i = 0; i < cal_samples; i++) {
      analogWrite(leds[led_num], i*2);
      delay(1);
      pwm_voltages[led_num][i] = read_voltage(led_num);
      if (i % 5 == 0) {
        Serial.print(i*2);
        Serial.print(" = ");
        Serial.println(pwm_voltages[led_num][i]);
      }
    }
  }
  Serial.println("\nCalibration Complete.");
}

uint16_t read_voltage(int led_num) {
  float sum = 0;
  for (int i = 0; i < num_samples; i++) {
    sum += analogRead(adcs[led_num]);
  }
  return bit_depth - (sum / num_samples);
}

void write_voltage(int led_num, float t) {
  targets[led_num] = t / 10 * 1024;
  if (targets[led_num] < pwm_voltages[led_num][cal_samples - 1]) {
    brightnesses[led_num] = 255;
  } else if (targets[led_num] > pwm_voltages[led_num][0]) {
    brightnesses[led_num] = 0;
  } else {
    for (int i = 0; i < cal_samples; i++) {
      if (pwm_voltages[led_num][i] < targets[led_num]) {
        brightnesses[led_num] = i*2;
        break;
      }
    }
  }
  analogWrite(leds[led_num], brightnesses[led_num]);
  delay(1);
  led_vs[led_num] = read_voltage(led_num);
}

void serialEvent() {
  buff = Serial.readStringUntil('\n');
  //  Serial.print("SERIAL EVENT: ");
  //  Serial.println(buff);
  if (buff.compareTo("c") == 0) {
    calibrate_led();
  } else if (buff.toFloat() != 0) {
    write_voltage(test_led, buff.toFloat());
    Serial.print("\nDuty Cycle (8 bit): ");
    Serial.println(brightnesses[test_led]);
    Serial.print("Voltage (V): ");
    Serial.println(led_vs[test_led]);
    Serial.print("Target  (V): ");
    Serial.println(targets[test_led]);
  }
}
void loop() {
  delay(10);
}
