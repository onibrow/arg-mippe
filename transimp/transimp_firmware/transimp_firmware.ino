#include <Wire.h>
#include <Adafruit_MCP4725.h>

const uint8_t MIPPE_LED = 2;

Adafruit_MCP4725 dac1;
Adafruit_MCP4725 dac2;
Adafruit_MCP4725 * dacs[2] = {&dac1, &dac2};

uint8_t adc[2] = {A1, A2};

int num_samples = 25;

const uint8_t VCC = 5;
const float adc_resolution = 1024.0;
const float dac_resolution = 4096.0;

char buff[50];
char args[50];

void setup(void) {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);
  
  dac1.begin(0x60);
  dac2.begin(0x63);
  for (int i = 0; i < 2; i++) {
    pinMode(adc[i], INPUT);
    dacs[i]->setVoltage(0, false);
  }
}

void info() {
  digitalWrite(MIPPE_LED, HIGH);
  Serial.println("tia");
}

void req() {
  digitalWrite(MIPPE_LED, HIGH);
  for (int j = 0; j < 2; j++) {
    double sum  = 0;
    for (int i = 0; i < num_samples; i++) {
      sum += analogRead(adc[j]);
    }
    Serial.print(sum / num_samples / adc_resolution * VCC, 3);
    Serial.print(",");
  }
  Serial.print("\n");
}

void write_dac(uint8_t i, uint16_t val) {
  digitalWrite(MIPPE_LED, HIGH);
  dacs[i]->setVoltage(val, false);
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

  if (strncmp(buff, "req", func) == 0) {
    req();
  } else if (strncmp(buff, "write_dac", func) == 0) {
    uint8_t comma = find_arg(buff, len, func);
    memcpy(args, &buff[func + 1], comma - func);
    args[comma - func - 1] = '\0';
    uint8_t channel = (uint8_t) atoi(args);
    memcpy(args, &buff[comma + 1], len - 1 - comma);
    args[len - 1 - comma - 1] = '\0';
    uint16_t val = (uint16_t) atoi(args);
    write_dac(channel, val);
  } else if (strncmp(buff, "info", func) == 0) {
    info();
  }
}

void loop() {
  digitalWrite(MIPPE_LED, LOW);
}
