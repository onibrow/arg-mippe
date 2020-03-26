import serial_select
import time

test_ser = serial_select.Cereal()

time.sleep(2)

test_ser.write_data("info\n".encode("ascii"))
print(test_ser.read_line())
