#include <Wire.h>
#include <Adafruit_MCP4725.h>

Adafruit_MCP4725 dac1;
Adafruit_MCP4725 dac2;

uint8_t adc1 = A1;
uint8_t adc2 = A2;

int num_samples = 200;

void setup(void) {
  Serial.begin(115200);
  dac1.begin(0x60);
  dac2.begin(0x63);
  pinMode(adc1, INPUT);
  pinMode(adc2, INPUT);

  dac1.setVoltage(0, false);
  dac2.setVoltage(0, false);
}

int take_reading(uint8_t adc) {
  double sum  = 0;
  for (int i = 0; i < num_samples; i++) {
    sum += analogRead(adc);
  }
  return sum / num_samples;
}

void loop(void) {
  Serial.println(take_reading(adc1));
  //  Serial.print(" ");
  //  Serial.println(take_reading(adc2));
//  delay(5);
}
