const uint8_t mux_a = 10;
const uint8_t mux_b = 9;

void setup() {
  // initialize both serial ports:
  Serial.begin(115200);
  while (!Serial) {
  };
  Serial1.begin(115200);
  pinMode(mux_a, OUTPUT);
  pinMode(mux_b, OUTPUT);
  digitalWrite(mux_a, LOW);
  digitalWrite(mux_b, LOW);
}

void loop() {
  // read from port 1, send to port 0:
  if (Serial1.available()) {
    int inByte = Serial1.read();
    Serial.write(inByte);
  }

  // read from port 0, send to port 1:
  if (Serial.available()) {
    int inByte = Serial.read();
    Serial1.write(inByte);
  }
}
