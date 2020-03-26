import cereal_port
import csv
import serial
import time
import sys
import glob
import datetime
from pytz import timezone
import readline

class oled_driver():
    def __init__(self, cereal):
        self.cereal = cereal
        self.oleds = [self.oled(1), self.oled(2), self.oled(3), self.oled(4)]
        self.next_req = [0, 0, 0, 0]
        time.sleep(1.75)
        self.setup_module()

    class oled():
        def __init__(self, n):
            self.num = n
            self.in_use = False
            self.routine = []
            self.mark = 0
            self.calibration = []

        def setup_oled(self):
            while (True):
                try:
                    user_input = input('OLED {} in use? (Y/n): '.format(self.num)).lower()
                    if (user_input != "" and user_input != "y" and user_input != "n"): raise ValueError
                    self.in_use = (user_input == "y" or user_input == "")
                    break
                except ValueError:
                    print("\nInvalid Input.")

        def set_calibration(self, cal):
            self.calibration = cal

        def voltage_to_cal_pwm(self, vol):
            if vol > 9:
                return 0
            elif vol < 0:
                return 255
            vol_bits = vol / 2 / 5 * 1024
            for i in range(len(self.calibration)):
                if (vol_bits > self.calibration[i]):
                    return i
            return 255

        def print_routine(self):
            printed_routine = ""
            if (len(self.routine) == 0):
                return "No routine programmed"
            for i in range(len(self.routine)):
                if (i == (len(self.routine) - 1)):
                    e = '.\n'
                else:
                    e = ', '
                v = "{0:.2f}".format(self.calibration[self.routine[i][0]] / 1024 * 10)
                s = "{0:.2f}".format(self.routine[i][1] * 1000)
                printed_routine += "{v}V for {s}ms{end}".format(v=v, s=s, end=e)
            return printed_routine

        def program_routine(self):
            print("Program a routine for OLED {}. Enter 'q' to save and finish.".format(self.num))
            print("Previous Routine: {}".format(self.print_routine()))
            while(True):
                try:
                    user_input_one = input('Desired Voltage (V): ')
                    if (user_input_one == 'q'): break
                    user_input_two = input('Time Frame (ms):     ')
                    if (user_input_one == 'q' or user_input_two == 'q'): break
                    if (float(user_input_one) < 0 or float(user_input_two) < 0): raise ValueError
                    self.routine += [(self.voltage_to_cal_pwm(float(user_input_one)), float(user_input_two) / 1000.0)]
                except ValueError:
                    print("\nInvalid Input.")
            print("New Routine: {}".format(self.print_routine()))

        def package_routine(self):
            packaged_routine = []
            for i in self.routine:
                packaged_routine += [("write_led({},{})".format(self.num, i[0]), i[1])]
            return packaged_routine

        def next_routine(self):
            n = self.routine[self.mark]
            self.mark = (self.mark + 1) % len(self.routine)
            return n

    def setup_module(self):
        for oled in self.oleds:
            oled.setup_oled()
            if (oled.in_use):
                print("Calibrating OLED {}".format(oled.num))
                cal = []
                self.cereal.write_data("calibrate_led({})".format(oled.num - 1).encode("ascii"))
                serial_data = self.cereal.read_line()
                while (serial_data != "CC"):
                    cal += [int(serial_data)]
                    serial_data = self.cereal.read_line()

                oled.set_calibration(cal)
                oled.program_routine()
                r = oled.next_routine()
                self.next_req[oled.num - 1] = r[1]
                self.write_led(oled.num, r[0])
                time.sleep(1)

    def next_routine(self, time):
        for i in range(len(self.next_req)):
            if (self.next_req[i] != 0 and self.next_req[i] < time):
                r = self.oleds[i].next_routine()
                self.next_req[i] = self.next_req[i] + r[1]
                self.write_led(i+1, r[0])

    def req_info(self):
        self.cereal.write_data(b'info()')
        serial_data = self.cereal.read_line()
        print(serial_data)
        return serial_data

    def write_led(self, oled_num, voltage):
        self.cereal.write_data("write_led({},{})\n".format(oled_num-1, voltage).encode("ascii"))

    def voltage_req(self):
        self.cereal.write_data(b'print_voltages()\n')
        serial_data = self.cereal.read_line()
        print(serial_data)
        return serial_data

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

def main():
    print("Startin Quad Channel OLED Driver Module")
    # pst = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M")
    # file_name  = rlinput('\nSave data as: \t', 'Diff_ADC_Data {}.csv'.format(pst))

    s = cereal_port.Cereal()
    print("")
    oled_module = oled_driver(s)
    input("\nPress Enter to start, Control+C to stop\n")
    start_time = time.time()
    prev_time = time.time()
    while(True):
        try:
            oled_module.next_routine(time.time() - start_time)
        except KeyboardInterrupt:
            s.close()
            print("\nElapsed Time:   {}".format(time.time() - start_time))
            break

if __name__ == '__main__':
    main()
