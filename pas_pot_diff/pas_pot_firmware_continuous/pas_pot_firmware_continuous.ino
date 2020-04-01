#include <Wire.h>
#include <MCP342x.h>
#include <SPI.h>

const uint8_t MIPPE_LED = 2;
const uint8_t CS  = 10;
MCP342x MCP(0);

long Voltage[4];
uint8_t ohms[4];

char buff[50];
char args[50];

void setup() {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);

  // MCP3424 Setup
  MCP.begin(0);
  MCP.setConfiguration(CH1, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);

  // AD8403 Setup (100k)
  SPI.begin();
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV32);
  pinMode(CS, OUTPUT);
  digitalWrite(CS, HIGH);
  default_dig_pot();
}

void info() {
  digitalWrite(MIPPE_LED, HIGH);
  Serial.print("paspot\n");
}

void default_dig_pot() {
  for (int i = 0; i < 4; i++) {
    write_pot(i, 128);
    ohms[i] = 128;
  }
}

void print_ohms() {
  digitalWrite(MIPPE_LED, HIGH);
  for (int i = 0; i < 4; i++) {
    Serial.print(ohms[i]);
    Serial.print(",");
  }
  Serial.print("\n");
}

void req() {
  digitalWrite(MIPPE_LED, HIGH);
  for (int i = 1; i <= 4; i++) {
    MCP.setConfiguration((CHANNELS) i, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);
    Voltage[i - 1] = MCP.measure();
  }
  Serial.print(Voltage[3] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[0] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[1] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[2] / 1000000000.0, 3); Serial.print(",\n");
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
  } else if (strncmp(buff, "write_pot", func) == 0) {
    uint8_t comma = find_arg(buff, len, func);
    memcpy(args, &buff[func + 1], comma - func);
    args[comma - func - 1] = '\0';
    uint8_t channel = (uint8_t) atoi(args);
    memcpy(args, &buff[comma + 1], len - 1 - comma);
    args[len - 1 - comma - 1] = '\0';
    uint8_t pot_val = (uint8_t) atoi(args);
    write_pot(channel, pot_val);
    ohms[channel] = pot_val;
  } else if (strncmp(buff, "print_ohms", func) == 0) {
    print_ohms();
  } else if (strncmp(buff, "info", func) == 0) {
    info();
  }
}

void loop() {
  digitalWrite(MIPPE_LED, LOW);
}

// Write to AD8403
void write_pot(uint8_t ch, uint8_t val) {
  digitalWrite(MIPPE_LED, HIGH);
  /* Addr: [9:8]
     Data: [7:0]*/
  uint8_t data = 255 - val;
  digitalWrite(CS, LOW);
  SPI.transfer(ch);
  SPI.transfer(data);
  digitalWrite(CS, HIGH);
}
