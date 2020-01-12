# Modular Integration Platform for Printed Electronics

##  Burn  In

Functional with indicator LEDs to burn in Arduino bootloader to any ISP contact pad enabled microcontroller board.

## MIPPE Base

Two Versions: ATMega328 \& ATMega32U4. The 328 does not have a built in USB interface and has a larger footprint size at a 32 pin QFP. The 32u4 does support native USB with a higher price tag and smaller footprint 44 pin QFN.

To flash, plug in the Burn In tool and run `bootloader.sh` script. Tap on a fully populated microcontrller enabled board using ISP contact pads and pogo pins. Select the appropriate microcontroller to start flashing. The 328 will only take about 15 seconds, while the 32u4 takes an upwards of 2 minutes

## OLED PMIC

An OLED driver that can do current control and limiting.
