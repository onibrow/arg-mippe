from mippe_mod_ui import mippe_module
import cereal_port
import helpers
import sched
import time

MIN_PERIOD = 1000

class tia_module(mippe_module):
    full_name = 'Transimpedance Amplifier Sensor Module'
    plot = True
    y_axis = 'Volts (V)'
    def __init__(self, num, cereal, scheduler, csvfile):
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
        print("Setting up TIA Module")
        for i in range(2):
            self.ch_names[i] = helpers.rlinput("Channel {} Name: ".format(i+1), self.ch_names[i])
            while (True):
                try:
                    user_input = float(helpers.rlinput('{} Bias Voltage (max 5): '.format(self.ch_names[i]), str(self.ch_biases[i])))
                    if (user_input < 0 or user_input > 5): raise ValueError
                    self.ch_biases[i] = user_input
                    self.write_voltage_to_dac(i, self.ch_biases[i])
                    break
                except ValueError:
                    print("\nBias must be between 0 and 5.")
        self.csvfile.write("{num},{name},{ch1} Bias: {ch1bias}V,{ch2} Bias: {ch2bias}V\n".format(num=self.module_num, name='tia',
            ch1=self.ch_names[0], ch1bias=self.ch_biases[0], ch2=self.ch_names[1], ch2bias=self.ch_biases[1]))

    def write_voltage_to_dac(self, ch, vol):
        return self.cereal.write_data("{}write_dac({},{})\n".format(self.module_num, ch, int(vol/5*4096)).encode("ascii"))

    def parse_vals(vals):
        r = []
        for x in vals:
            r += [round(int(helpers.clean_string(x)) / 1024.0 * 5, 3)]
        return r

def main():
    print("Starting Dual Channel Organic Photodiode Transimpedance Module")

    scheduler   = sched.scheduler(time.time, time.sleep)
    serial_port = cereal_port.Cereal()

    pst = helpers.get_datetime()
    file_name  = helpers.rlinput('\nSave data as: \t', 'TIA_Data {}.csv'.format(pst))

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
