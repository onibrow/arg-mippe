import csv
import cereal_port
import sched
import time
import readline
import time
import sys
import glob
import datetime
from pytz import timezone
import readline

class pas_pot_module():
    def __init__(self, cereal, scheduler):
        self.cereal = cereal
        self.sched  = scheduler

    def data_req(self):
        self.cereal.write_data(b'req\n')
        serial_data = self.ser.readline().decode("utf-8")
        return serial_data

    def req_info(self):
        self.cereal.write_data(b'info()')
        serial_data = self.cereal.read_line()
        return serial_data

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
