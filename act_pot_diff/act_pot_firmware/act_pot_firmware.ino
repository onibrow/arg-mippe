#include <Wire.h>
#include <MCP342x.h>

MCP342x MCPA(0);
MCP342x MCPB(2);

const uint8_t MIPPE_LED = 2;

char buff[50];
char args[50];

const uint8_t MAX_MEAS_BUFF = 25;
uint32_t meas_buff[MAX_MEAS_BUFF][8];
uint8_t next_meas = MAX_MEAS_BUFF;

void setup() {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);
  MCPA.begin(0);
  MCPB.begin(0);
  MCPA.setConfiguration(CH1, RESOLUTION_14_BITS, CONTINUOUS_MODE, PGA_X1);
  MCPB.setConfiguration(CH1, RESOLUTION_14_BITS, CONTINUOUS_MODE, PGA_X1);
}

void info() {
  digitalWrite(MIPPE_LED, HIGH);
  Serial.print("actpot\n");
}

void req() {
  digitalWrite(MIPPE_LED, HIGH);
  for (int i = 0; i < next_meas; i++) {
    Serial.print(meas_buff[i][3]); Serial.print(",");
    Serial.print(meas_buff[i][0]); Serial.print(",");
    Serial.print(meas_buff[i][1]); Serial.print(",");
    Serial.print(meas_buff[i][2]); Serial.print(",");
    Serial.print(meas_buff[i][7]); Serial.print(",");
    Serial.print(meas_buff[i][4]); Serial.print(",");
    Serial.print(meas_buff[i][5]); Serial.print(",");
    Serial.print(meas_buff[i][6]); Serial.print(",\n");
  }
  Serial.print("d\n");
  next_meas = 0;
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
  } else if (strncmp(buff, "start", func) == 0) {
    start();
  }
}

void start() {
  next_meas = 0;
}

void loop() {
  digitalWrite(MIPPE_LED, LOW);
  if (next_meas < MAX_MEAS_BUFF) {
    for (int i = 1; i <= 4; i++) {
      MCPA.setConfiguration((CHANNELS) i, RESOLUTION_14_BITS, CONTINUOUS_MODE, PGA_X1);
      MCPB.setConfiguration((CHANNELS) i, RESOLUTION_14_BITS, CONTINUOUS_MODE, PGA_X1);
      meas_buff[next_meas][i - 1]     = (uint32_t) MCPA.measure() / 10000;
      meas_buff[next_meas][4 + i - 1] = (uint32_t) MCPB.measure() / 10000;
    }
    next_meas++;
  }
}
