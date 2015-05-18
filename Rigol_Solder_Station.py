__author__ = 'RoGeorge'
#
# TODO: Port for Linux
# TODO: Add command line parameters for instruments IPs
# TODO: Add GUI
# TODO: Create executable distributions
#
import telnetlib
import time
import sys
import os

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
script_name = os.path.basename(sys.argv[0])

# Print usage
print
print "Usage:"
print script_name

def open_check(instrument, IP):
	# Check network response (ping) for oscilloscope
	response = os.system("ping -n 1 " + IP + " > nul")
	if response != 0:
		print
		print "No response pinging " + IP
		print "Check network cables and settings."
		print "You should be able to ping the", instrument

	# Open a telnet session for oscilloscope
	tn = telnetlib.Telnet(IP, port)
	tn.write("*idn?")                       # ask for instrument ID
	instrument_id = tn.read_until("\n", 1)

	# # Check if oscilloscope is set to accept LAN commands
	# if instrument_id == "command error":
	# 	print instrument_id
	# 	print "Check the", instrument, "settings."
	# 	print "Utility -> IO Setting -> RemoteIO -> LAN must be ON"
	# 	sys.exit("ERROR")
	#
	# Check if instrument is indeed a Rigol DS1000Z series
	# id_fields = instrument_id.split(",")
	# print instrument
	# print IP
	# print id_fields[company]
	# print id_fields[model]
	# if (id_fields[company] != "RIGOL TECHNOLOGIES") or \
	# 	(id_fields[model][:3] != "DS1") or (id_fields[model][-1] != "Z"):
	# 	print
	# 	print "ERROR: No Rigol from series DS1000Z found at ", IP_DS1104Z
	# 	sys.exit("ERROR")

	print instrument, "ID:"
	print instrument_id

	return tn

tn_oscilloscope = open_check("oscilloscope", IP_DS1104Z)
# tn_power_source = open_check("power source", IP_DP832)

# Set the oscilloscope
# tn_oscilloscope.write("MEASure:ITEM VAVG, CHANnel4")
# tn_oscilloscope.write("*opc?")                     # operation(s) completed ?
# tn_oscilloscope.read_until("\n", 1)                # wait max 1s for an answer
print "step 1"
# tn.write("display:data?")
# print "Receiving..."
# buff = tn.read_until("\n", small_wait)
#
# # Just in case the transfer did not complete in the expected time
# if buff[-1] != '\n':
# 	print "Error: Answer from instrument took longer then", small_wait, "second(s)."
# 	sys.exit("ERROR")
#
# # Set the power source


# Temperature control loop
steps = 100
print steps
t1 = time.time()
for i in range(0, steps):
	# Read thermocouple
	tn_oscilloscope.write("MEASure:ITEM? VAVG, CHANnel4")
	buff = tn_oscilloscope.read_until("\n", small_wait)
	print buff

	# Compute running average
	# Convert mV to *C
	# Compute next output voltage
	# Set new voltage
	# Loop until a stop request encountered


t2 = time.time()
ms_per_step = (t2 - t1)/steps * 1000
print "ms/step =", ms_per_step
# Close telnet sessions
# tn_power_source.close()
tn_oscilloscope.close()


# IP_DP832 = "192.168.1.4"
# port = 5555
#
# min_volt = float(0)
# max_volt = float(10)
# mV = 1000
# ms = 1000
# steps_per_volt = 10
#
# tn = telnetlib.Telnet(IP_DP832, port)
# tn.write("*idn?")                       # interrogate instrument ID
# print tn.read_until("\n", 1)
#
# # TODO - quit if no answer from instrument
#
# tn.write("output:state ch1, on")        # power on ch1
# tn.write("*opc?")
# tn.read_until("\n", 1)
#
# t1 = time.time()
#
# for i in range(int(min_volt*mV), int(max_volt*mV), mV/steps_per_volt):
# 	# tn.write("volt " + str(float(i)/mV))  # set ch1 output voltage
# 	v = str(float(random.randint(min_volt*mV, max_volt*mV))/mV)
# 	print v
# 	tn.write("volt " + v)  # set ch1 output voltage
# 	tn.write("*opc?")                     # operation(s) completed ?
# 	tn.read_until("\n", 1)                # wait max 1s for an answer
#
# v = "5.000"
# print v
# tn.write("volt " + v)  # set ch1 output voltage
# tn.write("*opc?")                     # operation(s) completed ?
# tn.read_until("\n", 1)                # wait max 1s for an answer
#
# t2 = time.time()
#
# total_steps = (max_volt - min_volt) * steps_per_volt
# total_time = (t2 - t1) * ms
# print "The average execution time for a telnet LXI command was",
# print "%.3f" % (total_time / total_steps), "ms."
#
# tn.close()