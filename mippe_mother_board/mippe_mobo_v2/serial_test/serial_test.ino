const uint8_t mux_a = 10;
const uint8_t mux_b = 9;

char buff[50];

void setup() {
  Serial.begin(115200);
  while (!Serial) {
  };
  Serial1.begin(115200);
  pinMode(mux_a, OUTPUT);
  pinMode(mux_b, OUTPUT);
  digitalWrite(mux_a, HIGH);
  digitalWrite(mux_b, HIGH);
}

void loop() {
  if (Serial.available()) {
    size_t r = Serial.readBytesUntil('\n', buff, 50);
    char s = buff[0];
    switch (s) {
      case 48:
        digitalWrite(mux_a, LOW);
        digitalWrite(mux_b, LOW);
        break;
      case 49:
        digitalWrite(mux_a, HIGH);
        digitalWrite(mux_b, LOW);
        break;
      case 50:
        digitalWrite(mux_a, LOW);
        digitalWrite(mux_b, HIGH);
        break;
      default:
        digitalWrite(mux_a, HIGH);
        digitalWrite(mux_b, HIGH);
        break;
    }
    for (int i = 1; i < r; i++) {
      Serial1.write(buff[i]);
    }
    Serial1.write('\n');
  }

  if (Serial1.available()) {
    size_t r = Serial1.readBytesUntil('\n', buff, 50);
    for (int i = 0; i < r; i++) {
      Serial.write(buff[i]);
    }
    Serial.write("\n");
  }
}
