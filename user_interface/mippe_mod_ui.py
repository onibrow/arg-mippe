import cereal_port
import helpers
import sched
import time

class mippe_module(object):
    full_name = 'Generic Mippe Module'
    plot = False
    y_axis = 'Data'
    def __init__(self, num, cereal, scheduler, csvfile):
        self.module_num = str(num)
        self.cereal = cereal
        self.sched  = scheduler
        self.csvfile = csvfile
        self.setup_module()

    def setup_module(self):
        print("Setting up Generic Mippe Module")

    def req_info(self):
        self.cereal.write_data('{}info()\n'.format(self.module_num).encode("ascii"))
        serial_data = self.cereal.read_line()
        return serial_data

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

    def parse_vals(vals):
        return [x * 1.0 for x in vals]
