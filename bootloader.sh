echo "Bootloader Tool v1.0"
echo "Seiya Ono Fa'19"
echo ""
echo "Select Board to burn in"
echo "[1] Pro Mni (5V 16MHz)"
echo "[2] Leonardo (5V)"
echo "[3] Uno"
read -p 'Board: ' board

if [ $board -eq 1 ]
then
  /home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/bin/avrdude -C/home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/etc/avrdude.conf -v -patmega328p -cstk500v1 -P/dev/ttyACM0 -b19200 -e -Ulock:w:0x3F:m -Uefuse:w:0xFD:m -Uhfuse:w:0xDA:m -Ulfuse:w:0xFF:m
  /home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/bin/avrdude -C/home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/etc/avrdude.conf -v -patmega328p -cstk500v1 -P/dev/ttyACM0 -b19200 -Uflash:w:/home/onibrow/.arduino15/packages/arduino/hardware/avr/1.8.2/bootloaders/atmega/ATmegaBOOT_168_atmega328.hex:i -Ulock:w:0x0F:m
elif [ $board -eq 2 ]
then
  /usr/lib/arduino-1.8.10/hardware/tools/avr/bin/avrdude -C/usr/lib/arduino-1.8.10/hardware/tools/avr/etc/avrdude.conf -v -patmega32u4 -cstk500v1 -P/dev/ttyACM0 -b19200 -e -Ulock:w:0x3F:m -Uefuse:w:0xcb:m -Uhfuse:w:0xd8:m -Ulfuse:w:0xff:m
  /usr/lib/arduino-1.8.10/hardware/tools/avr/bin/avrdude -C/usr/lib/arduino-1.8.10/hardware/tools/avr/etc/avrdude.conf -v -patmega32u4 -cstk500v1 -P/dev/ttyACM0 -b19200 -Uflash:w:/usr/lib/arduino-1.8.10/hardware/arduino/avr/bootloaders/caterina/Caterina-Leonardo.hex:i -Ulock:w:0x2F:m
elif [ $board -eq 3 ]
then
  /home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/bin/avrdude -C/home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/etc/avrdude.conf -v -patmega328p -cstk500v1 -P/dev/ttyACM0 -b19200 -e -Ulock:w:0x3F:m -Uefuse:w:0xFD:m -Uhfuse:w:0xDE:m -Ulfuse:w:0xFF:m 
  /home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/bin/avrdude -C/home/onibrow/.arduino15/packages/arduino/tools/avrdude/6.3.0-arduino17/etc/avrdude.conf -v -patmega328p -cstk500v1 -P/dev/ttyACM0 -b19200 -Uflash:w:/home/onibrow/.arduino15/packages/arduino/hardware/avr/1.8.2/bootloaders/optiboot/optiboot_atmega328.hex:i -Ulock:w:0x0F:m
fi
