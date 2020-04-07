const uint8_t MIPPE_LED = 2;
j
char buff[50];
char args[50];

const uint8_t MAX_MEAS_BUFF = 16;
uint32_t meas_buff[MAX_MEAS_BUFF]
uint8_t next_meas = MAX_MEAS_BUFF;

// GLOBAL VARIABLES

void setup() {
  pinMode(MIPPE_LED, OUTPUT);
  digitalWrite(MIPPE_LED, HIGH);
  Serial.begin(115200);

  // START MODULE CONFIGURATION

}

void info() {
  digitalWrite(MIPPE_LED, HIGH);
  Serial.print("mippe_mod\n");
}

void req() {
  digitalWrite(MIPPE_LED, HIGH);
  for (int i = 0; i < next_meas; i++) {
    Serial.print(meas_buff[i]); Serial.print("\n");
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
    // TAKE MEASUREMENTS
    meas_buff[next_meas] = next_meas;
    next_meas++;
  }
}
