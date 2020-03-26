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

class transimp_amp():
    def __init__(self, serial_port):
        self.ser = serial_port
        self.ser_write_flag = sys.platform.startswith('win')
        self.ch1 = 'OPD1'
        self.ch2 = 'OPD2'
        self.period = 0.016
        self.ch1_bias = 0
        self.ch2_bias = 0
        self.setup_module()

    def setup_module(self):
        self.ch1 = rlinput("\nChannel 1 Name: ", self.ch1)
        self.ch2 =   rlinput("Channel 2 Name: ", self.ch2)

        while (True):
            try:
                user_input = int(rlinput('Sampling period in ms (min 16): ', str(int(self.period * 1000))))
                if (user_input < 16): raise ValueError
                self.period = user_input / 1000.0
                break
            except ValueError:
                print("\nSampling period must be an integer greater than 16.")

        while (True):
            try:
                user_input = float(rlinput('{} Bias Voltage (max 5): '.format(self.ch1), str(self.ch1_bias)))
                if (user_input < 0 or user_input > 5): raise ValueError
                self.ch1_bias = user_input
                self.serial_write("w1{}".format(self.ch1_bias).encode())
                break
            except ValueError:
                print("\nBias must be between 0 and 5.")

        while (True):
            try:
                user_input = float(rlinput('{} Bias Voltage (max 5): '.format(self.ch2), str(self.ch2_bias)))
                if (user_input < 0 or user_input > 5): raise ValueError
                self.ch2_bias = user_input
                self.serial_write("w2{}".format(self.ch2_bias).encode())
                break
            except ValueError:
                print("\nBias must be between 0 and 5.")

    def serial_write(self, data):
        if self.ser_write_flag:
            self.ser.write([data, ])
        else:
            self.ser.write(data)

    def data_req(self):
        self.serial_write(b'req\n')
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
    print("Starting Dual Channel Organic Photodiode Transimpedance Module")
    pst = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M")
    file_name  = rlinput('\nSave data as: \t', 'Diff_ADC_Data {}.csv'.format(pst))

    s = select_serial_port()
    t_module = transimp_amp(s)
    input("\nPress Enter to start, Control+C to stop\n")
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
