const uint8_t MIPPE_LED = 2;
const uint8_t leds[4] = {9, 6, 5, 3};           // the PWM pin the LED is attached to
const uint8_t adcs[4] = {A0, A1, A2, A3};          // Reading in LED Voltage / 2
const uint8_t num_samples = 250; // Number of averages
const int bit_depth = 1023;

int led_vs[4] = {0, 0, 0, 0};

char buff[50];
char args[50];

void setup() {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);

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
    led_vs[i] = read_voltage(i);
    Serial.print(led_vs[i]);
    Serial.print(", ");
  }
  Serial.print("\n");
}

void write_led(uint8_t led, uint8_t pwm) {
  digitalWrite(MIPPE_LED, HIGH);
  analogWrite(leds[led], pwm);
}

uint16_t find_func(char * buff, uint8_t len) {
  for (int i = 0; i < len; i++) {
    if (buff[i] == '(') {
      return i;
    }
  }
  return len;
}

uint16_t find_arg(char * buff, uint8_t len, uint8_t start) {
  for (int i = start; i < len; i++) {
    if (buff[i] == ',') {
      return i;
    }
  }
  return len;
}

void serialEvent() {
  size_t len = Serial.readBytesUntil('\n', buff, 50);
  uint8_t func = find_func(buff, len);

  if (strncmp(buff, "calibrate_led", func) == 0) {
    memcpy(args, &buff[func+1], len-1 - func + 1);
    uint8_t led = (uint8_t) atoi(args);
    Serial.print(led);
    calibrate_led(led);
  } else if (strncmp(buff, "write_led", func) == 0) {
    uint8_t comma = find_arg(buff, len, func);

    memcpy(args, &buff[func + 1], comma - func);
    args[comma - func - 1] = '\0';
    uint8_t led = (uint8_t) atoi(args);

    memcpy(args, &buff[comma + 1], len - 1 - comma);
    args[len - 1 - comma - 1] = '\0';
    uint8_t pwm = (uint8_t) atoi(args);

    write_led(led, pwm);
  } else if (strncmp(buff, "print_voltages", func) == 0) {
    print_voltages();
  } else if (strncmp(buff, "info", func) == 0) {
    info();
  }
}

void loop() {
  digitalWrite(MIPPE_LED, LOW);
}
