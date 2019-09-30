# Modular Integration Platform for Printed Electronics

Rev A:

##  Burn  In

Functional with indicator LEDs

## MIPPE Base

Not functional - wrong microcontroller (168P instead of 328P).

To flash:

```
avrdude -p m168p -P /dev/ttyACM0 -c avrisp flash:w:/lib/arduino-1.8.10/hardware/arduino/avr/bootloaders/atmega/ATmegaBOOT_168_atmega328_pro_8MHz.hex avrdude.conf
```
