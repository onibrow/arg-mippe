#include <Wire.h>
#include <MCP342x.h>

MCP342x MCPA(0);
MCP342x MCPB(2);

const uint8_t MIPPE_LED = 2;
long Voltage[2][4];

char buff[50];
char args[50];

void setup() {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);
  MCPA.begin(0);
  MCPB.begin(0);
  MCPA.setConfiguration(CH1, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);
  MCPB.setConfiguration(CH1, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);
}

void info() {
  digitalWrite(MIPPE_LED, HIGH);
  Serial.print("actpot\n");
}

void req() {
  digitalWrite(MIPPE_LED, HIGH);
  for (int i = 1; i <= 4; i++) {
    MCPA.setConfiguration((CHANNELS) i, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);
    MCPB.setConfiguration((CHANNELS) i, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);
    Voltage[0][i - 1] = MCPA.measure();
    Voltage[1][i - 1] = MCPB.measure();
  }
  Serial.print(Voltage[0][3] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[0][0] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[0][1] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[0][2] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[1][3] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[1][0] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[1][1] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[1][2] / 1000000000.0, 3); Serial.print(",\n");
}

uint16_t find_func(char * buff, uint8_t len) {
  for (int i = 0; i < len; i++) {
    if (buff[i] == '(') {
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
  } else if (strncmp(buff, "info", func) == 0) {
    info();
  }
}

void loop() {
  digitalWrite(MIPPE_LED, LOW);
}
