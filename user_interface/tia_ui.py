import cereal_port
from live_plotter import live_plotter
import numpy as np

import csv
import sched
import time

import datetime
from pytz import timezone
import readline

MIN_PERIOD = 1000

class tia_module():
    def __init__(self, num, cereal, scheduler, csvfile):
        print("\nSetting up TIA Module")
        time.sleep(1);
        self.module_num = str(num)
        self.cereal = cereal
        self.sched  = scheduler
        self.csvfile = csvfile
        self.ch_names = ['OPD1', 'OPD2']
        self.ch_biases = [0, 0]
        self.period = MIN_PERIOD / 1000.0
        self.setup_module()

    def setup_module(self):
        """
        while (True):
            try:
                user_input = int(rlinput('Sampling period in ms (min {}): '.format(MIN_PERIOD), str(int(self.period * 1000))))
                if (user_input < MIN_PERIOD): raise ValueError
                self.period = user_input / 1000.0
                break
            except ValueError:
                print("\nSampling period must be an integer greater than {}.".format(MIN_PERIOD))
        """

        for i in range(2):
            self.ch_names[i] = rlinput("Channel {} Name: ".format(i+1), self.ch_names[i])
            while (True):
                try:
                    user_input = float(rlinput('{} Bias Voltage (max 5): '.format(self.ch_names[i]), str(self.ch_biases[i])))
                    if (user_input < 0 or user_input > 5): raise ValueError
                    self.ch_biases[i] = user_input
                    self.write_voltage_to_dac(i, self.ch_biases[i])
                    break
                except ValueError:
                    print("\nBias must be between 0 and 5.")

    def log_channel_names(self):
        to_write = self.module_num
        for c in self.ch_names:
            to_write += c + "."
        self.csvfile.write(to_write)

    def req_info(self):
        self.cereal.write_data('{}info()\n'.format(self.module_num).encode("ascii"))
        serial_data = self.cereal.read_line()
        return serial_data

    def next_routine(self):
        s = time.time()
        self.sched.enter(self.period, 1, self.next_routine)
        self.cereal.write_data('{}req\n'.format(self.module_num).encode("ascii"))
        to_write = ""
        serial_data = self.cereal.read_line()
        while (serial_data != 'd'):
            to_write += self.module_num + serial_data + "\n"
            serial_data = self.cereal.read_line()
        self.csvfile.write(to_write)
        print('Routine time: {}'.format(time.time() - s))

    def start_routine(self):
        self.cereal.write_data('{}start()\n'.format(self.module_num).encode("ascii"))
        self.sched.enter(self.period, 1, self.next_routine)

    def write_voltage_to_dac(self, ch, vol):
        return self.cereal.write_data("{}write_dac({},{})\n".format(self.module_num, ch, int(vol/5*4096)).encode("ascii"))

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

def main():
    print("Starting Dual Channel Organic Photodiode Transimpedance Module")

    scheduler   = sched.scheduler(time.time, time.sleep)
    serial_port = cereal_port.Cereal()

    pst = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M:%S")
    file_name  = rlinput('\nSave data as: \t', 'TIA_Data {}.csv'.format(pst))

    with open(file_name, 'w') as csvfile:
        tia = tia_module(1, serial_port, scheduler, csvfile)

        input("\nPress Enter to start, Control+C to stop\n")
        tia.start_routine()
        start = time.time()

        try:
            while (True):
                next_ev = scheduler.run(False)
                if next_ev is not None:
                    time.sleep(min(1, next_ev))
                else:
                    pass
        except KeyboardInterrupt:
            csvfile.write(str(time.time() - start))
            if (not scheduler.empty()):
                queue = scheduler.queue
                for e in queue:
                    scheduler.cancel(e)
            serial_port.close()
            raise KeyboardInterrupt

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExitting...")
