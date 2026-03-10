/*
 * Arduino fan control firmware for MAS thermal prototype.
 *
 * Expects serial commands: FAN,fan_id,speed\n
 *   - fan_id: 0, 1, or 2 (index into fanPins)
 *   - speed: 0-255 (PWM)
 *
 * Pins 3, 5, 6 are PWM-capable on most Arduino boards.
 */

const int fanPins[3] = {3, 5, 6};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 3; i++) {
    pinMode(fanPins[i], OUTPUT);
  }
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');

    if (cmd.startsWith("FAN,")) {
      int firstComma = cmd.indexOf(',');
      int secondComma = cmd.indexOf(',', firstComma + 1);

      int fanId = cmd.substring(firstComma + 1, secondComma).toInt();
      int speed = cmd.substring(secondComma + 1).toInt();

      if (fanId >= 0 && fanId < 3) {
        analogWrite(fanPins[fanId], speed);
      }
    }
  }
}
