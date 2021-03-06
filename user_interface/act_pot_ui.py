from mippe_mod_ui import mippe_module
import cereal_port
import helpers
import sched
import time

class act_pot_module(mippe_module):
    full_name = 'Active Potentiometric Sensor Module'
    plot = False
    y_axis = 'Volts (V)'
    def __init__(self, num, cereal, scheduler, csvfile):
        self.module_num = str(num)
        self.cereal = cereal
        self.sched  = scheduler
        self.csvfile = csvfile
        self.ch_names = ['Ch1', 'Ch2', 'Ch3', 'Ch4', 'Ch5', 'Ch6', 'Ch7', 'Ch8']
        self.setup_module()

    def setup_module(self):
        print("Setting up Active Sensor Module")
        for i in range(8):
            self.ch_names[i] = helpers.rlinput("Channel {} Name: ".format(i+1), self.ch_names[i])
        self.csvfile.write("{num},{name},{ch0},{ch1},{ch2},{ch3},{ch4},{ch5},{ch6},{ch7}\n".format(
            num=self.module_num, name='tia',
            ch0=self.ch_names[0], ch1=self.ch_names[1], ch2=self.ch_names[2], ch3=self.ch_names[3],
            ch4=self.ch_names[4], ch5=self.ch_names[5], ch6=self.ch_names[6], ch7=self.ch_names[7]))

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
    file_name  = helpers.rlinput('\nSave data as: \t', 'Data_Act_Pot {}.csv'.format(pst))

    with open(file_name, 'w') as csvfile:
        act = act_pot_module(0, serial_port, scheduler, csvfile)

        input("\nPress Enter to start, Control+C to stop\n")
        act.start_routine()
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
