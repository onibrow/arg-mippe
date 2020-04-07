import cereal_port
import helpers
import sched
import time

from act_pot_ui import act_pot_module
from pas_pot_ui import pas_pot_module
from oled_ui    import oled_module
from tia_ui     import tia_module

class MIPPE():
    def __init__(self, cereal, scheduler, csvfile):
        self.cereal = cereal
        self.scheduler = scheduler
        self.csvfile = csvfile
        self.loaded_modules = [None, None, None]
        self.setup_module()

    def setup_module(self):
        self.csvfile.write("MIPPE Data\n")
        print("Loading Modules...\n")
        for i in range(3):
            self.cereal.write_data('{}info\n'.format(i).encode("ascii"))
            data = self.cereal.read_line()
            if (data == 'actpot'):
                self.loaded_modules[i] = act_pot_module(i, self.cereal, self.scheduler, self.csvfile)
            elif (data == 'paspot'):
                self.loaded_modules[i] = pas_pot_module(i, self.cereal, self.scheduler, self.csvfile)
            elif (data == 'oled'):
                self.loaded_modules[i] = oled_module(i, self.cereal, self.scheduler, self.csvfile)
            elif (data == 'tia'):
                self.loaded_modules[i] = tia_module(i, self.cereal, self.scheduler, self.csvfile)
            else:
                self.loaded_modules[i] = None
                print("Module {} Not Identified.".format(i+1))
                self.csvfile.write("{},None\n".format(i))
            print("")

    def start_routine(self):
        for x in self.loaded_modules:
            if (x != None):
                x.start_routine()
                time.sleep(0.3)

def main():
    print("+----------------------------------------------------------+")
    print("|   Modular Integration Platform for Printed Electronics   |")
    print("|                      Seiya Ono '20                       |")
    print("+----------------------------------------------------------+")

    scheduler   = sched.scheduler(time.time, time.sleep)
    serial_port = cereal_port.Cereal()
    pst = helpers.get_datetime()
    file_name  = 'data/' + helpers.rlinput('\nSave data as: \t', 'MIPPE_Data {}.csv'.format(pst))

    with open(file_name, 'w') as csvfile:

        mippe = MIPPE(serial_port, scheduler, csvfile)

        input("\nPress Enter to start, Control+C to stop")
        start = time.time()
        mippe.start_routine()
        try:
            scheduler.run(True)
        except KeyboardInterrupt:
            csvfile.write("{0:.2f}".format(time.time() - start))
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
