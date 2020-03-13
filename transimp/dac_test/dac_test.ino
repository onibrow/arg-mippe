#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac1;
Adafruit_MCP4725 dac2;

void setup(void) {
  Serial.begin(115200);
  dac1.begin(0x60);
  dac2.begin(0x63);

  dac1.setVoltage(0, false);
  dac2.setVoltage(0, false);
}

void loop(void) {
}
