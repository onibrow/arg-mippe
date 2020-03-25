const uint8_t MIPPE_LED = 2;
const uint8_t leds[4] = {9, 6, 5, 3};           // the PWM pin the LED is attached to
const uint8_t adcs[4] = {A0, A1, A2, A3};          // Reading in LED Voltage / 2
const uint8_t num_samples = 250; // Number of averages
const int bit_depth = 1023;

int led_vs[4] = {0, 0, 0, 0};

String buff;
String func;
String args;

void setup() {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);

  buff.reserve(20);
  func.reserve(20);
  args.reserve(20);

  for (int led_num = 0; led_num < 4; led_num++) {
    pinMode(leds[led_num], OUTPUT);
    analogWrite(leds[led_num], 255);
    pinMode(adcs[led_num], INPUT);
  }
}

void info() {
  digitalWrite(MIPPE_LED, HIGH);
  Serial.println("oled");
}

void calibrate_led(uint8_t led_num) {
  digitalWrite(MIPPE_LED, HIGH);
  for (int i = 0; i < 256; i++) {
    analogWrite(leds[led_num], i);
    delay(1);
    Serial.println(read_voltage(led_num));
  }
  Serial.println("CC");
}

uint16_t read_voltage(int led_num) {
  digitalWrite(MIPPE_LED, HIGH);
  long sum = 0;
  for (int i = 0; i < num_samples; i++) {
    sum += analogRead(adcs[led_num]);
  }
  return bit_depth - (sum / num_samples);
}

void print_voltages() {
  digitalWrite(MIPPE_LED, HIGH);
  for (int i = 0; i < 4; i++) {
    Serial.print(led_vs[i]);
    Serial.print(", ");
  }
  Serial.print("\n");
}

void write_led(uint8_t led, uint8_t pwm) {
  digitalWrite(MIPPE_LED, HIGH);
  analogWrite(leds[led], pwm);
  delay(1);
  led_vs[led] = read_voltage(led);
}

void loop() {
  digitalWrite(MIPPE_LED, LOW);
  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');
    func = buff.substring(0, buff.indexOf('('));

    if (func.equals("calibrate_led")) {
      args = buff.substring(buff.indexOf('(') + 1, buff.indexOf(')'));
      uint8_t led = (uint8_t) args.substring(0,  args.indexOf(',')).toInt();
      calibrate_led(led);
    } else if (func.equals("write_led")) {
      args = buff.substring(buff.indexOf('(') + 1, buff.indexOf(')'));
      uint8_t led = (uint8_t) args.substring(0,  args.indexOf(',')).toInt();
      uint8_t pwm = (uint8_t) args.substring(args.indexOf(',') + 1).toInt();
      write_led(led, pwm);
    } else if (func.equals("print_voltages")) {
      print_voltages();
    } else if (func.equals("info")) {
      info();
    }
  }
}
