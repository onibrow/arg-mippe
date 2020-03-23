/*
 * 1999250000 = 2
*/


#include <Wire.h>
#include <MCP342x.h>

MCP342x MCPA(0);

MCP342x MCPB(2);

long Voltage[2][4];
String buff = String("deadbuffdead");
int num_samples = 1;

void setup() {
  MCPA.begin(0);
  MCPB.begin(0);
  MCPA.setConfiguration(CH1, RESOLUTION_16_BITS, ONE_SHOT_MODE, PGA_X1); // Channel 1, 16 bits resolution, one-shot mode, amplifier gain = 1
  MCPB.setConfiguration(CH1, RESOLUTION_16_BITS, ONE_SHOT_MODE, PGA_X1);
  Serial.begin(115200); // start serial for output
  //  Serial.print("MCP3424 Configuration Complete!\n");
}

void loop() {
  if (Serial.available()) {
    buff = Serial.readStringUntil('\n');
    //    Serial.println(buff);
    for (int i = 1; i <= 4; i++) {
      MCPA.setConfiguration((CHANNELS) i, RESOLUTION_16_BITS, ONE_SHOT_MODE, PGA_X1);
      MCPB.setConfiguration((CHANNELS) i, RESOLUTION_16_BITS, ONE_SHOT_MODE, PGA_X1);
      long cumsum_voltage_A = 0;
      long cumsum_voltage_B = 0;
      for (int j = 0; j < num_samples; j++) {
        MCPA.newConversion();
        MCPB.newConversion();
        cumsum_voltage_A += MCPA.measure();
        cumsum_voltage_B += MCPB.measure();
      }
      Voltage[0][i - 1] = -1 * cumsum_voltage_A / num_samples;
      Voltage[1][i - 1] = -1 * cumsum_voltage_B / num_samples;
    }
    if (buff.equals("req")) {
      Serial.print(Voltage[1][2]); Serial.print(",");
      Serial.print(Voltage[1][1]); Serial.print(",");
      Serial.print(Voltage[1][0]); Serial.print(",");
      Serial.print(Voltage[1][3]); Serial.print(",");
      Serial.print(Voltage[0][2]); Serial.print(",");
      Serial.print(Voltage[0][1]); Serial.print(",");
      Serial.print(Voltage[0][0]); Serial.print(",");
      Serial.print(Voltage[0][3]); Serial.print(",\n");
    }
  }
}
