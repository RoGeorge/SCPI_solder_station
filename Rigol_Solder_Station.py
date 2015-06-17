__author__ = 'RoGeorge'
#
# TODO: Port for Linux
# TODO: Add PID
# TODO: Add command line parameters for instruments IPs
# TODO: Add GUI
# TODO: Create versioned executable distributions
#
from time import *
from sys import *
import os

from functions import connect_verify, init_oscilloscope, init_power_supply, \
											command


# Update the next lines for your own default settings:
path_to_save = ""
save_format = "PNG"

IP_DS1104Z = "192.168.1.3"
IP_DP832 = "192.168.1.4"

min_volt = float(0)
max_volt = float(10)

# Rigol/LXI specific constants
port = 5555

small_wait = 1

company = 0
model = 1
serial = 2

# Check parameters
script_name = os.path.basename(argv[0])

# Print usage
print
print "Usage:"
print script_name

# Connect and check instruments
tn_oscilloscope = connect_verify("oscilloscope", IP_DS1104Z, port)
tn_power_source = connect_verify("power supply", IP_DP832, port)

# Initialize instruments
init_oscilloscope(tn_oscilloscope)
init_power_supply(tn_power_source)

print "Preheating..."
# Check preheat
voltage = 5
command(tn_power_source, "SOURce2:VOLTage " + str(voltage))

# Calibrate PID

# Temperature control loop
t1 = time()
while True:
	# Read thermocouple
	tn_oscilloscope.write("MEASure:ITEM? VAVG, CHANnel4")
	buff = tn_oscilloscope.read_until("\n", small_wait)

	if buff[0] < "0" or buff[0] > "9":
		print "bing !", buff
		buff = "0.01\n"

	# Convert thermocouple voltage readings to *C
	t = abs(int(1000000 * float(buff[:-1]))/1000.0)

	# Compute running average

	# Compute next output voltage
	if t < 10:
		voltage += 0.1
	if t > 10.5:
		voltage -= 0.1
	if voltage > 24:
		voltage = 24

	# Set new voltage
	command(tn_power_source, "SOURce2:VOLTage " + "{0:.1f}".format(voltage))

	# Loop until a stop request encountered

	t2 = time()
	ms_per_step = (t2 - t1) * 1000
	t1 = t2
	print "ms/step =", ms_per_step

# power off
command(tn_power_source, "OUTPut CH2, OFF")

# Close telnet sessions and exit
tn_oscilloscope.close()
tn_power_source.close()
print "Normal exit. Bye!"
