import csv
import serial
import time
import sys
import datetime
from pytz import timezone
import readline

class Diff_ADC():
    def __init__(self, serial_port):
        self.ser = serial_port

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
