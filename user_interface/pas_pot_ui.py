import cereal_port
from live_plotter import live_plotter
import numpy as np

import csv
import sched
import time

import datetime
from pytz import timezone
import readline

MIN_PERIOD = 100

class pas_pot_module():
    def __init__(self, num, cereal, scheduler, csvfile):
        self.module_num = str(num)
        self.cereal = cereal
        self.sched  = scheduler
        self.csvfile = csvfile
        self.ch_names = ['Ch1', 'Ch2', 'Ch3', 'Ch4']
        self.ch_res   = [    0,     0,     0,     0]
        self.period = MIN_PERIOD / 1000.0
        self.setup_module()

    def setup_module(self):
        print("Setting up Passive Sensor Module")

        while (True):
            try:
                user_input = int(rlinput('Sampling period in ms (min {}): '.format(MIN_PERIOD), str(int(self.period * 1000))))
                if (user_input < MIN_PERIOD): raise ValueError
                self.period = user_input / 1000.0
                break
            except ValueError:
                print("\nSampling period must be an integer greater than {}.".format(MIN_PERIOD))

        for i in range(4):
            print("Channel {}:".format(i+1))
            self.ch_names[i] = rlinput("Name: ".format(i), self.ch_names[i])
            while (True):
                try:
                    self.ch_res[i]   = int(int(rlinput("Reference Resistance (0 - 100k): ", self.ch_res[i])) / 100000.0 * 255)
                    if (self.ch_res[i] < 0 or self.ch_res[i] > 255): raise ValueError
                    print("Writing Closeset Resistance {:.2f} Ohms".format(self.ch_res[i] / 255.0 * 100000))
                    self.write_pot(i, self.ch_res[i])
                    break
                except ValueError:
                    print("\nResistance must be between 0 and 100k")

    def log_channel_names(self):
        to_write = self.module_num
        for c in self.ch_names:
            to_write += c + "."
        self.csvfile.write(to_write)

    def data_req(self):
        self.cereal.write_data('{}req\n'.format(self.module_num).encode("ascii"))
        serial_data = self.cereal.read_line()
        return serial_data

    def req_info(self):
        self.cereal.write_data('{}info()\n'.format(self.module_num).encode("ascii"))
        serial_data = self.cereal.read_line()
        return serial_data

    def next_routine(self):
        self.sched.enter(self.period, 1, self.next_routine)
        data = self.module_num +  self.data_req() + "\n"
        self.csvfile.write(data)

    def start_routine(self):
        self.sched.enter(self.period, 1, self.next_routine)

    def write_pot(self, ch, val):
        self.cereal.write_data('{}write_pot({},{})\n'.format(self.module_num, ch, val).encode("ascii"))

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

def main():
    print("Starting Quadchannel Differential ADC Data Logger")

    scheduler   = sched.scheduler(time.time, time.sleep)
    serial_port = cereal_port.Cereal()

    pst = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M:%S")
    file_name  = rlinput('\nSave data as: \t', 'Data_OLED {}.csv'.format(pst))

    with open(file_name, 'w') as csvfile:
        pas = pas_pot_module(1, serial_port, scheduler, csvfile)

        input("\nPress Enter to start, Control+C to stop\n")
        pas.start_routine()
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
