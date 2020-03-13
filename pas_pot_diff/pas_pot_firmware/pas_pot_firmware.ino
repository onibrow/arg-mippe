/*
   1999250000 = 2
*/
#include <Wire.h>
#include <MCP342x.h>
#include <SPI.h>

const uint8_t CS  = 10;
MCP342x MCP(0);

long Voltage[4];
String buff;
int num_samples = 1;

void setup() {
  Serial.begin(115200); // start serial for output
  buff.reserve(20);
  // MCP3424 Setup
  MCP.begin(0);
  MCP.setConfiguration(CH1, RESOLUTION_16_BITS, ONE_SHOT_MODE, PGA_X1); // Channel 1, 16 bits resolution, one-shot mode, amplifier gain = 1

  // AD8403 Setup
  SPI.begin();
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV32);
  pinMode(CS, OUTPUT);
  digitalWrite(CS, HIGH);
  default_dig_pot();
}

void default_dig_pot() {
  for (int i = 0; i < 4; i++) {
    write_dig_pot(CS, i, 128);
  }
}
void loop() {
  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');
    //    Serial.println(buff);

    if (buff.equals("req")) {
      for (int i = 1; i <= 4; i++) {
        MCP.setConfiguration((CHANNELS) i, RESOLUTION_16_BITS, ONE_SHOT_MODE, PGA_X1);
        long cumsum_voltage = 0;
        for (int j = 0; j < num_samples; j++) {
          MCP.newConversion();
          cumsum_voltage += MCP.measure();
        }
        Voltage[i - 1] = -1 * cumsum_voltage / num_samples;
      }
      Serial.print(Voltage[2] / 1000000000.0); Serial.print(",");
      Serial.print(Voltage[1] / 1000000000.0); Serial.print(",");
      Serial.print(Voltage[0] / 1000000000.0); Serial.print(",");
      Serial.print(Voltage[3] / 1000000000.0); Serial.print(",\n");
    }
    else if (buff.charAt(0) == 'w') {
      uint8_t channel = (uint8_t) buff.charAt(1);
      uint8_t val = buff.substring(2).toInt();
      switch (channel) {
        case 48:
          channel = 0;
          break;
        case 49:
          channel = 1;
          break;
        case 50:
          channel = 2;
          break;
        case 51:
          channel = 3;
          break;
        default:
          channel = NULL;
      }
      Serial.print("Writing ");
      Serial.print(val);
      Serial.print(" to ");
      Serial.println(channel);
      write_dig_pot(CS, channel, val);
    }
  }
}

// Write to AD8400
void write_dig_pot(uint8_t cs, uint8_t ch, uint8_t val) {
  /* Addr: [9:8]
     Data: [7:0]

     For single Channel AD8400, Addr is 0b00 */
  uint8_t data = val;
  // transfer payload
  digitalWrite(cs, LOW);
  SPI.transfer(ch);
  SPI.transfer(data);
  digitalWrite(cs, HIGH);
}
