import serial
import sys
import glob

BAUD_RATE = 115200
TIMEOUT = 2
STOPBITS = serial.STOPBITS_ONE

class Cereal():

    def __init__(self):
        self.sys_write_flag = sys.platform.startswith('win')
        self.ser_port = Cereal.select_serial_port()

    def list_ports():
        """Lists serial ports

        Raises:
        EnvironmentError:
          On unsupported or unknown platforms
        Returns:
          A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

    def select_serial_port():
        ports = Cereal.list_ports()
        if ports:
            print("\nAvailable serial ports:")
            for (i, p) in enumerate(ports):
                print("%d) %s" % (i + 1, p))
        else:
            print("\nNo ports available. Check serial connection and try again.")
            print("Exiting...")
            quit()

        ser_port_sel = -1
        while(ser_port_sel == -1):
            try:
                selection = input("Select the port to use (1,2,...): ")
                ser_port_sel = int(selection)
                if (ser_port_sel == 0): quit()
                elif (ser_port_sel > len(ports) or ser_port_sel < 0):
                    raise ValueError
            except ValueError:
                ser_port_sel = -1
                print("Invalid Port Number.")
        ser = serial.Serial(ports[ser_port_sel - 1], BAUD_RATE, timeout = TIMEOUT, stopbits = STOPBITS)
        return ser

    def write_data(self, data):
        if self.sys_write_flag:
            self.ser_port.write([data, ])
        else:
            self.ser_port.write(data)

    def read_line(self):
        return self.ser_port.readline().decode("utf-8").strip()

    def close(self):
        self.ser_port.close()
