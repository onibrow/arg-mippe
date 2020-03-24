#include <Wire.h>
#include <MCP342x.h>
#include <SPI.h>

const uint8_t CS  = 10;
MCP342x MCP(0);

long Voltage[4];
String buff;
String func;
String args;

uint8_t ohms[4];

void setup() {
  Serial.begin(115200);
  buff.reserve(20);
  func.reserve(20);
  args.reserve(20);

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

void default_dig_pot() {
  for (int i = 0; i < 4; i++) {
    write_pot(i, 128);
    ohms[i] = 128;
  }
}

void print_ohms() {
  for (int i = 0; i < 4; i++) {
    Serial.print(ohms[i]);
    Serial.print(", ");
  }
  Serial.print("\n");
}

void req() {
  for (int i = 1; i <= 4; i++) {
    MCP.setConfiguration((CHANNELS) i, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);
    Voltage[i - 1] = MCP.measure();
  }
  Serial.print(Voltage[2] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[1] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[0] / 1000000000.0, 3); Serial.print(",");
  Serial.print(Voltage[3] / 1000000000.0, 3); Serial.print(",\n");
}
void loop() {
  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');
    func = buff.substring(0, buff.indexOf('('));
    args = buff.substring(buff.indexOf('(') + 1, buff.indexOf(')'));

    if (func.equals("req")) {
      req();
    } else if (func.equals("write_pot")) {
      uint8_t channel = (uint8_t) args.substring(0,  args.indexOf(',')).toInt();
      uint8_t pot_val = (uint8_t) args.substring(args.indexOf(',') + 1).toInt();
      write_pot(channel, pot_val);
      ohms[channel - 1] = pot_val;
    } else if (func.equals("print_ohms")) {
      print_ohms();
    }
  }
}

// Write to AD8403
void write_pot(int ch, int val) {
  /* Addr: [9:8]
     Data: [7:0]*/
  uint8_t data = val;
  digitalWrite(CS, LOW);
  SPI.transfer(ch);
  SPI.transfer(data);
  digitalWrite(CS, HIGH);
}
