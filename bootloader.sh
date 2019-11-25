echo "Bootloader Tool v1.0"
echo "Seiya Ono Fa'19"
echo ""
echo "Select Board to burn in"
echo "[1] Pro Mni (3.3V)"
echo "[2] Leonardo (5V)"
read -p 'Board: ' board

if [ $board -eq 1 ]
then
  /usr/lib/arduino-1.8.10/hardware/tools/avr/bin/avrdude -C/usr/lib/arduino-1.8.10/hardware/tools/avr/etc/avrdude.conf -v -patmega328p -cstk500v1 -P/dev/ttyACM0 -b19200 -e -Ulock:w:0x3F:m -Uefuse:w:0xFD:m -Uhfuse:w:0xDE:m -Ulfuse:w:0xFF:m
elif [ $board -eq 2 ]
then
  /usr/lib/arduino-1.8.10/hardware/tools/avr/bin/avrdude -C/usr/lib/arduino-1.8.10/hardware/tools/avr/etc/avrdude.conf -v -patmega32u4 -cstk500v1 -P/dev/ttyACM0 -b19200 -e -Ulock:w:0x3F:m -Uefuse:w:0xcb:m -Uhfuse:w:0xd8:m -Ulfuse:w:0xff:m
  /usr/lib/arduino-1.8.10/hardware/tools/avr/bin/avrdude -C/usr/lib/arduino-1.8.10/hardware/tools/avr/etc/avrdude.conf -v -patmega32u4 -cstk500v1 -P/dev/ttyACM0 -b19200 -Uflash:w:/usr/lib/arduino-1.8.10/hardware/arduino/avr/bootloaders/caterina/Caterina-Leonardo.hex:i -Ulock:w:0x2F:m
fi
