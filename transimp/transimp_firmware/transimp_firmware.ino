#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac1;
Adafruit_MCP4725 dac2;
Adafruit_MCP4725 * dacs[2] = {&dac1, &dac2};

uint8_t adc1 = A1;
uint8_t adc2 = A2;

int num_samples = 50;

const uint8_t VCC = 5;
const float adc_resolution = 1024.0;
const float dac_resolution = 4096.0;

String buff = "";

void setup(void) {
  Serial.begin(115200);
  buff.reserve(50);
  dac1.begin(0x60);
  dac2.begin(0x63);
  pinMode(adc1, INPUT);
  pinMode(adc2, INPUT);

  dac1.setVoltage(0, false);
  dac2.setVoltage(0, false);
}

float take_reading(uint8_t adc) {
  double sum  = 0;
  for (int i = 0; i < num_samples; i++) {
    sum += analogRead(adc);
  }
  return sum / num_samples / adc_resolution * VCC;
}

void loop(void) {
  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');

    if (buff.equals("req")) {
      Serial.print(take_reading(adc1), 3); Serial.print(",");
      Serial.print(take_reading(adc2), 3); Serial.print(",\n");
    }
    else if (buff.charAt(0) == 'w') {
      uint8_t channel = (uint8_t) buff.charAt(1);
      uint16_t val = (uint16_t) (buff.substring(2).toFloat() * dac_resolution / 5);
      switch (channel) {
        case 49:
          channel = 1;
          break;
        case 50:
          channel = 2;
          break;
        default:
          channel = 0;
          break;
      }
      if (channel != 0) {
        Serial.print("Writing ");
        Serial.print(val);
        Serial.print(" to ");
        Serial.println(channel);
        dacs[channel - 1]->setVoltage(val, false);
      }
    }
  }
}
