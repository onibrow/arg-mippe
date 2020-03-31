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

String buff;
String func;
String args;

void setup(void) {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);

  buff.reserve(20);
  func.reserve(20);
  args.reserve(20);

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

void loop(void) {
  digitalWrite(MIPPE_LED, LOW);
  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');
    func = buff.substring(0, buff.indexOf('('));

    if (func.equals("req")) {
      req();
    } else if (func.equals("write_dac")) {
      args = buff.substring(buff.indexOf('(') + 1, buff.indexOf(')'));
      uint8_t dac = (uint8_t) args.substring(0,  args.indexOf(',')).toInt();
      uint16_t val = (uint16_t) args.substring(args.indexOf(',') + 1).toInt();
      write_dac(dac, val);
    } else if (func.equals("info")) {
      info();
    }
  }
}
