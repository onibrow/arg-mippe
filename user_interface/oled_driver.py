import cereal_port
import sched
import time
import readline

DEBUG = True
default_r = [[(104, 0.25), (255, 0.75)], [(255, 0.25), (102, 0.25), (255, 0.5)], [(255, 0.5), (106, 0.25), (255, 0.25)], [(255, 0.75), (101, 0.25)]]

class oled_module():
    def __init__(self, cereal, scheduler):
        self.cereal = cereal
        self.sched  = scheduler
        self.oled_cals = [[], [], [], []]
        self.oled_routines = [[], [], [], []]
        self.oled_inuse = [False, False, False, False]
        self.oled_marks = [0, 0, 0, 0]
        self.oled_volts = [0, 0, 0, 0]
        time.sleep(2)
        self.setup_module()

    def setup_module(self):
        if (DEBUG):
            self.oled_routines = default_r
            self.oled_inuse = [True, True, True, True]
        else:
            for oled in range(4):
                self.setup_oled(oled)

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
            self.cereal.write_data("calibrate_led({})".format(num).encode("ascii"))
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
        self.cereal.write_data(b'info()')
        serial_data = self.cereal.read_line()
        return serial_data

    def write_led(self, oled_num, voltage):
        self.cereal.write_data("write_led({},{})\n".format(oled_num, voltage).encode("ascii"))

    def voltage_req(self):
        self.cereal.write_data(b'print_voltages()\n')
        serial_data = self.cereal.read_line()
        return serial_data

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

def main():
    print("Startin Quad Channel OLED Driver Module")
    # pst = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M")
    # file_name  = rlinput('\nSave data as: \t', 'Diff_ADC_Data {}.csv'.format(pst))

    scheduler   = sched.scheduler(time.time, time.sleep)
    serial_port = cereal_port.Cereal()

    print("")

    oled = oled_module(serial_port, scheduler)

    input("\nPress Enter to start, Control+C to stop\n")
    oled.start_routine()
    try:
        scheduler.run(blocking=True)
    except KeyboardInterrupt:
        serial_port.close()

if __name__ == '__main__':
    main()
