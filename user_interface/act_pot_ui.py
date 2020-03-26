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
    selection = input("Select the port to use: ")
    # Note: seems like timeout of 1 doesn't work
    ser = serial.Serial(ports[int(selection) - 1], BAUD_RATE, timeout = TIMEOUT, stopbits = STOPBITS)
    return ser

class Diff_ADC():
    def __init__(self, serial_port):
        self.ser = serial_port

    def serial_write(self, data):
        if sys.platform.startswith('win'):
            self.ser.write([data, ])
        else:
            self.ser.write(data)

    def serial_request(self):
        self.serial_write(b'deaddead\n')
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
    print("Starting Quadchannel Differential ADC Data Logger")
    pst = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M")
    file_name  = rlinput('\nSave data as: \t', 'Diff_ADC_Data {}.csv'.format(pst))
    try:
        delay = int(rlinput('\nSample period in ms (min 300): \t', '300')) / 1000.0
    except ValueError:
        print("\nSample period must be an integer in milliseconds. Exiting...")
        quit()
    ch1 = rlinput("\nChannel 1 Name: \t", 'Na')
    ch2 = rlinput("Channel 2 Name: \t", 'K')
    ch3 = rlinput("Channel 3 Name: \t", 'Unused')
    ch4 = rlinput("Channel 4 Name: \t", 'NH4')

    s = select_serial_port()
    mcp = Diff_ADC(s)
    print("\nInitializing MCP3424...")
    time.sleep(3)
    input("\nPress Enter to start, Control+C to stop\n")
    with open(file_name, 'w') as csvfile:
        start_time = time.time()
        i = 0
        prev_time = time.time()
        csvfile.write("{}, {}, {}, {},\n".format(ch1, ch2, ch3, ch4))
        while(True):
            if (time.time() - prev_time > delay):
                prev_time = time.time()
                try:
                    next_line = mcp.serial_request()
                    csvfile.write(next_line)
                    i += 1
                except:
                    mcp.serial_close()
                    csvfile.close()
                    print("\nElapsed Time:   {}".format(time.time() - start_time))
                    print("Num Samples: {}".format(i))
                    break

if __name__ == '__main__':
    main()
