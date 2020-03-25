import csv
import serial
import time
import sys
import glob
import datetime
from pytz import timezone
import readline

BAUD_RATE = 115200
TIMEOUT = 2
STOPBITS = serial.STOPBITS_ONE

def serial_ports():
    """Lists serial ports

    Raises:
    EnvironmentError:
      On unsupported or unknown platforms
    Returns:
      A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def select_serial_port():
    ports = serial_ports()
    if ports:
        print("\nAvailable serial ports:")
        for (i, p) in enumerate(ports):
            print("%d) %s" % (i + 1, p))
    else:
        print("\nNo ports available. Check serial connection and try again.")
        print("Exiting...")
        quit()

    ser_port_sel = -1
    while(ser_port_sel == -1):
        try:
            selection = input("Select the port to use (1,2,...): ")
            ser_port_sel = int(selection)
            if (ser_port_sel == 0): quit()
            elif (ser_port_sel > len(ports) or ser_port_sel < 0):
                raise ValueError
        except ValueError:
            ser_port_sel = -1
            print("Invalid Port Number.")
    ser = serial.Serial(ports[ser_port_sel - 1], BAUD_RATE, timeout = TIMEOUT, stopbits = STOPBITS)
    return ser

class oled_driver():
    def __init__(self, serial_port):
        self.ser = serial_port
        self.ser_write_flag = sys.platform.startswith('win')
        self.oleds = [self.oled(1), self.oled(2), self.oled(3), self.oled(4)]
        self.setup_module()

    class oled():
        def __init__(self, n):
            self.num = n
            self.in_use = False
            self.routine = []
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
                s = "{0:.2f}".format(self.routine[i][1])
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
                    self.routine += [(self.voltage_to_cal_pwm(float(user_input_one)), float(user_input_two))]
                except ValueError:
                    print("\nInvalid Input.")
            print("New Routine: {}".format(self.print_routine()))

        def package_routine(self):
            packaged_routine = []
            for i in self.routine:
                packaged_routine += [("write_led({},{})".format(self.num, i[0]), i[1])]
            return packaged_routine

    def setup_module(self):
        for oled in self.oleds:
            oled.setup_oled()
            if (oled.in_use):
                print("Calibrating OLED {}".format(oled.num))
                cal = []
                self.serial_write("calibrate_led({})".format(oled.num - 1).encode("ascii"))
                serial_data = self.serial_read()
                while (serial_data != "CC"):
                    cal += [int(serial_data)]
                    serial_data = self.serial_read()

                oled.set_calibration(cal)
                oled.program_routine()

    def serial_write(self, data):
        if self.ser_write_flag:
            self.ser.write([data, ])
        else:
            self.ser.write(data)

    def req_info(self):
        self.serial_write(b'info()')
        serial_data = self.ser.readline().decode("utf-8")
        print(serial_data)
        return serial_data


    def serial_read(self):
        serial_data = self.ser.readline().decode("utf-8")
        # print(serial_data)
        return serial_data.strip()

    def voltage_req(self):
        self.serial_write(b'print_voltages()\n')
        serial_data = self.ser.readline().decode("utf-8")
        print(serial_data)
        return serial_data

    def serial_close(self):
        self.ser.close()

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

    s = select_serial_port()
    print("")
    time.sleep(1.5)
    oled_module = oled_driver(s)
    input("\nPress Enter to start, Control+C to stop\n")
    quit()
    with open(file_name, 'w') as csvfile:
        start_time = time.time()
        i = 0
        prev_time = time.time()
        csvfile.write("{}, {},\n".format(t_module.ch1, t_module.ch2))
        while(True):
            try:
                if (time.time() - prev_time > t_module.period):
                    prev_time = time.time()
                    next_line = t_module.data_req()
                    csvfile.write(next_line)
                    i += 1
            except:
                t_module.serial_close()
                csvfile.close()
                print("\nElapsed Time:   {}".format(time.time() - start_time))
                print("Num Samples: {}".format(i))
                break

if __name__ == '__main__':
    main()
