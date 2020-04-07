from mippe_mod_ui import mippe_module
import cereal_port
import helpers
import sched
import time

MIN_PERIOD = 1000

class pas_pot_module(mippe_module):
    full_name = 'Passive Potentiometric Sensor Module'
    plot = True
    y_axis = 'Volts (V)'
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
        for i in range(4):
            print("Channel {}:".format(i+1))
            self.ch_names[i] = helpers.rlinput("Name: ", self.ch_names[i])
            while (True):
                try:
                    self.ch_res[i]   = int(int(helpers.rlinput("Reference Resistance (0 - 100k): ", str(self.ch_res[i]))) / 100000.0 * 256 - 1)
                    if (self.ch_res[i] == -1): self.ch_res[i] = 0
                    if (self.ch_res[i] < 0 or self.ch_res[i] > 255): raise ValueError
                    print("Writing Closeset Resistance {:.2f} Ohms".format((self.ch_res[i]+1) / 256.0 * 100000))
                    self.write_pot(i, self.ch_res[i])
                    break
                except ValueError:
                    self.ch_res[i] = 0
                    print("\nResistance must be between 0 and 100k")
        self.csvfile.write("{num},{name},{name1} Ref: {res1} Ohms,{name2} Ref: {res2} Ohms,{name3} Ref: {res3} Ohms,{name4} Ref: {res4} Ohms\n".format(num=self.module_num,name='pas',
            name1=self.ch_names[0], res1="{:.2f}".format((self.ch_res[0]+1) / 256.0 * 100000),
            name2=self.ch_names[1], res2="{:.2f}".format((self.ch_res[1]+1) / 256.0 * 100000),
            name3=self.ch_names[2], res3="{:.2f}".format((self.ch_res[2]+1) / 256.0 * 100000),
            name4=self.ch_names[3], res4="{:.2f}".format((self.ch_res[3]+1) / 256.0 * 100000)))

    def next_routine(self):
        self.sched.enter(self.period, 1, self.next_routine)
        self.cereal.write_data('{}req\n'.format(self.module_num).encode("ascii"))
        to_write = ""
        serial_data = self.cereal.read_line()
        while (serial_data != 'd'):
            to_write += self.module_num + "," + serial_data + "\n"
            serial_data = self.cereal.read_line()
        self.csvfile.write(to_write)

    def start_routine(self):
        self.cereal.write_data('{}start()\n'.format(self.module_num).encode("ascii"))
        self.sched.enter(self.period, 1, self.next_routine)

    def write_pot(self, ch, val):
        self.cereal.write_data('{}write_pot({},{})\n'.format(self.module_num, ch, val).encode("ascii"))

    def parse_vals(vals):
        r = []
        for x in vals:
            r += [int(helpers.clean_string(x)) / 100000.0]
        return r

def main():
    print("Starting Quadchannel Differential ADC Data Logger")

    scheduler   = sched.scheduler(time.time, time.sleep)
    serial_port = cereal_port.Cereal()

    pst = helpers.get_datetime()
    file_name  = helpers.rlinput('\nSave data as: \t', 'Pas_Pot_Data {}.csv'.format(pst))

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
