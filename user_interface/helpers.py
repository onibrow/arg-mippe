import glob
import readline
import datetime
import matplotlib.pyplot as plt
import numpy as np
import re
from scipy.signal import butter, lfilter, freqz
import csv
from pytz import timezone

from act_pot_ui import act_pot_module
from pas_pot_ui import pas_pot_module
from oled_ui    import oled_module
from tia_ui     import tia_module

Vcc = 5
module_code_dict = {
        'act' : act_pot_module,
        'oled': oled_module,
        'pas' : pas_pot_module,
        'tia' : tia_module}

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

def get_datetime():
    return datetime.datetime.now(tz=datetime.timezone.utc).astimezone(timezone('US/Pacific')).strftime("%m-%d-%Y %H:%M:%S")

def select_csv_file():
    csv_file_list = glob.glob('*.csv')
    selection = 0
    while(selection < 1 or selection > len(csv_file_list)):
        for i in range(len(csv_file_list)):
            print("{}) {}".format(i+1, csv_file_list[i]))
        try:
            selection = int(input("Select CSV File to Visualize (1,2,...): "))
        except ValueError:
            selection = 0
        if (selection < 1 or selection > len(csv_file_list)):
            print("\nInvalid Input")
    return csv_file_list[selection - 1]

class module_data(object):
    def __init__(self, row):
        self.mod_num = int(row[0])
        self.code = row[1]
        self.ref_class = module_code_dict[self.code]
        self.full_name = self.ref_class.full_name
        self.to_plot = self.ref_class.plot
        self.y_axis = self.ref_class.y_axis
        self.ch_names = row[2:]
        self.ch_data = []
        self.active_channels = []
        self.setup_module_data()

    def setup_module_data(self):
        if (self.to_plot):
            sel = 'x'
            while (sel != '' and sel != 'y' and sel != 'n'):
                sel = input("Plot {}? [Y/n]: ".format(self.full_name)).lower()
                if (sel != '' and sel != 'y' and sel != 'n'):
                    print("\nInvalid Selection.")
            if (sel == 'y' or sel == ''):
                self.to_plot = True
            else:
                self.to_plot = False

        for _ in range(len(self.ch_names)):
            self.ch_data += [[]]

        if (self.to_plot):
            for y in range(len(self.ch_names)):
                sel = 'x'
                while (sel != '' and sel != 'y' and sel != 'n'):
                    sel = input("Plot {}? [Y/n]: ".format(self.ch_names[y])).lower()
                    if (sel != '' and sel != 'y' and sel != 'n'):
                        print("\nInvalid Selection.")
                if (sel == 'y' or sel == ''):
                    self.active_channels += [True]
                else:
                    self.active_channels += [False]

    def __str__(self):
        s = "Mod Num:  {}\nName:     {}\nData Len: {}\n".format(self.mod_num, self.full_name, len(self.ch_data[0]))
        s2 = ""
        if (self.to_plot):
            for i in range(len(self.ch_names)):
                if (self.active_channels[i]):
                    s2 += "Ch{}:      {}\n".format(i+1, self.ch_names[i])
        return "{}{}".format(s, s2).strip()

    def add_data(self, row):
        if (len(row) != len(self.ch_names)):
            raise ValueError("Data legnth does not match number of channels")
        parsed_row = self.ref_class.parse_vals(row)
        for i in range(len(parsed_row)):
            self.ch_data[i] += [parsed_row[i]]

    def set_xvals(self, time):
        data_len = len(self.ch_data[0])
        self.xvals = np.linspace(0, time, data_len)
        if (self.code == 'tia'):
            for x in range(len(self.ch_names)):
                self.ch_data[x] = butter_lowpass_filter(3 * self.ch_data[x], 5, data_len / time, order=5)[data_len:data_len*2]

def split_data():
    data      = {}
    file_name = select_csv_file()
    print("")
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile)
        if (reader.__next__()[0] != 'MIPPE Data'):
            print("Not Valid MIPPE Data")
            return 1
        for row in reader:
            if (row[1] != 'None'):
                data[int(row[0])] = module_data(row)
                print("")
            if (reader.line_num > 3):
                break
        for row in reader:
            if (len(row) == 1):
                total_time = float(row[0])
                pass
            try:
                data[int(row[0])].add_data(row[1:])
            except ValueError:
                pass
    for d in data.values():
        print(d)
        d.set_xvals(total_time)
        print("")
    return data

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def plot_data(data):
    for module in data.values():
        if (module.to_plot):
            fig, ax = plt.subplots(figsize=(10,5))
            for i in range(len(module.active_channels)):
                if (module.active_channels[i]):
                    ax.set_title(module.full_name)
                    ax.plot(module.xvals, module.ch_data[i], label=module.ch_names[i])
                    ax.set_xlabel("Time (s)")
                    ax.set_ylabel(module.y_axis)
                    ax.legend()

def clean_string(s):
    return re.sub("[^0-9]", "", s)
