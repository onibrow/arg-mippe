/*
   1999250000 = 2
*/


#include <Wire.h>
#include <MCP342x.h>

MCP342x MCPA(0);

MCP342x MCPB(2);

long Voltage[2][4];
String buff = String("deadbuffdead");

void setup() {
  MCPA.begin(0);
  MCPB.begin(0);
  MCPA.setConfiguration(CH1, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1); // Channel 1, 16 bits resolution, one-shot mode, amplifier gain = 1
  MCPB.setConfiguration(CH1, RESOLUTION_12_BITS, CONTINUOUS_MODE, PGA_X1);
  Serial.begin(115200); // start serial for output
  //  Serial.print("MCP3424 Configuration Complete!\n");
}

void loop() {
  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');

    if (buff.equals("req")) {
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
  }
}
