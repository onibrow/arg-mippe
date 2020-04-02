import cereal_port
import helpers
import sched
import time

DEBUG = True
default_r = [[(0, 0.25), (255, 0.75)], [(255, 0.25), (0, 0.25), (255, 0.5)], [(255, 0.5), (0, 0.25), (255, 0.25)], [(255, 0.75), (0, 0.25)]]

class oled_module(object):
    full_name  = 'OLED Module'
    plot = False
    y_axis = 'Volts (V)'
    def __init__(self, num, cereal, scheduler, csvfile):
        self.module_num = str(num)
        self.cereal = cereal
        self.sched  = scheduler
        self.csvfile = csvfile
        self.oled_cals = [[], [], [], []]
        self.oled_routines = [[], [], [], []]
        self.oled_inuse = [False, False, False, False]
        self.oled_marks = [0, 0, 0, 0]
        self.oled_volts = [0, 0, 0, 0]
        self.oled_names = ['OLED1', 'OLED2', 'OLED3', 'OLED4']
        time.sleep(2)
        self.setup_module()

    def setup_module(self):
        print("Setting up OLED Module")
        if (DEBUG):
            self.oled_routines = default_r
            self.oled_inuse = [True, True, True, True]
        else:
            for oled in range(4):
                self.setup_oled(oled)
        self.csvfile.write("{num},{name},{oled1},{oled2},{oled3},{oled4}\n".format(num=self.module_num, name='oled',
            oled1=self.oled_names[0],
            oled2=self.oled_names[1],
            oled3=self.oled_names[2],
            oled4=self.oled_names[3]))

    def setup_oled(self, num):
        while (True):
            try:
                user_input = input('OLED {} in use? (Y/n): '.format(num+1)).lower()
                if (user_input != "" and user_input != "y" and user_input != "n"): raise ValueError
                self.oled_inuse[num] = (user_input == "y" or user_input == "")
                break
            except ValueError:
                print("\nInvalid Input.")

        if (self.oled_inuse[num]):
            self.calibrate_oled(num)
            self.program_routine(num)
            time.sleep(1)

    def calibrate_oled(self, num):
            print("Calibrating OLED {}".format(num+1))
            cal = []
            self.cereal.write_data("{}calibrate_led({})\n".format(self.module_num, num).encode("ascii"))
            serial_data = self.cereal.read_line()
            while (serial_data != "CC"):
                cal += [int(serial_data)]
                serial_data = self.cereal.read_line()
            self.oled_cals[num] = cal

    def voltage_to_cal_pwm(self, vol, num):
        if vol > 9:
            return 0
        elif vol < 0:
            return 255
        vol_bits = vol / 2 / 5 * 1024
        for i in range(len(self.oled_cals[num])):
            if (vol_bits > self.oled_cals[num][i]):
                return i
        return 255

    def print_routine(self, num):
        printed_routine = ""
        if (len(self.oled_routines[num]) == 0):
            return "No routine programmed"
        for i in range(len(self.oled_routines[num])):
            if (i == (len(self.oled_routines[num]) - 1)):
                e = '.\n'
            else:
                e = ', '
            v = "{0:.2f}".format(self.oled_cals[num][self.oled_routines[num][i][0]] / 1024 * 10)
            s = "{0:.2f}".format(self.oled_routines[num][i][1] * 1000)
            printed_routine += "{v}V for {s}ms{end}".format(v=v, s=s, end=e)
        return printed_routine

    def program_routine(self, num):
        print("Program a routine for OLED {}. Enter 'q' to save and finish.".format(num+1))
        print("Previous Routine: {}".format(self.print_routine(num)))
        while(True):
            try:
                user_input_one = input('Desired Voltage (V): ')
                if (user_input_one == 'q'): break
                user_input_two = input('Time Frame (ms):     ')
                if (user_input_one == 'q' or user_input_two == 'q'): break
                if (float(user_input_one) < 0 or float(user_input_two) < 0): raise ValueError
                self.oled_routines[num] += [(self.voltage_to_cal_pwm(float(user_input_one), num), float(user_input_two) / 1000.0)]
            except ValueError:
                print("\nInvalid Input.")
        print("New Routine: {}".format(self.print_routine(num)))

    def next_routine(self, num):
        n = self.oled_routines[num][self.oled_marks[num]]
        self.sched.enter(n[1], 1, self.next_routine, argument=(num,))
        self.write_led(num, n[0])
        self.oled_volts[num] = n[0]
        self.oled_marks[num]= (self.oled_marks[num] + 1) % len(self.oled_routines[num])

    def start_routine(self):
        for i in range(4):
            if (self.oled_inuse[i]):
                self.next_routine(i)

    def req_info(self):
        self.cereal.write_data('{}info()\n'.format(self.module_num).encode("ascii"))
        serial_data = self.cereal.read_line()
        return serial_data

    def write_led(self, oled_num, voltage):
        self.cereal.write_data("{}write_led({},{})\n".format(self.module_num,oled_num, voltage).encode("ascii"))

    def voltage_req(self):
        self.cereal.write_data('{}print_voltages()\n'.format(self.module_num).encode("ascii"))
        serial_data = self.cereal.read_line()
        return serial_data

    def parse_vals(vals):
        return 'None'

def main():
    print("Startin Quad Channel OLED Driver Module")

    scheduler   = sched.scheduler(time.time, time.sleep)
    serial_port = cereal_port.Cereal()

    oled = oled_module(2, serial_port, scheduler, None)

    input("\nPress Enter to start, Control+C to stop\n")
    oled.start_routine()
    start = time.time()

    try:
        while (True):
            next_ev = scheduler.run(False)
            if next_ev is not None:
                time.sleep(min(1, next_ev))
            else:
                pass
    except KeyboardInterrupt:
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
