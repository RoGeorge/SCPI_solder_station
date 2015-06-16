__author__ = 'RoGeorge'

import platform
import os
import telnetlib
import sys


# Check network response (ping)
def ping_IP(instrument, IP):
	if platform.system() == "Windows":
		response = os.system("ping -n 1 " + IP + " > nul")
	else:
		response = os.system("ping -c 1 " + IP + " > /dev/null")

	if response != 0:
		print
		print "No response pinging " + IP
		print "Check network cables and settings."
		print "You should be able to ping the " + instrument + "."


# Open a telnet session for Rigol instrument
def connect_to(instrument, IP, port):
	tn = telnetlib.Telnet(IP, port)
	# Ask for instrument ID
	tn.write("*idn?")
	instrument_id = tn.read_until("\n", 1)

	COMPANY = 0
	MODEL = 1
	id_fields = instrument_id.split(",")

	# Check if the instrument is set to accept LAN commands
	if id_fields[COMPANY] != "RIGOL TECHNOLOGIES":
		print instrument_id
		print "Non Rigol:,", instrument, "or the", instrument, "does not accept LAN commands."
		print "Check the", instrument, "settings."
		if instrument == "oscilloscope":
			print "Utility -> IO Setting -> RemoteIO -> LAN must be ON"
		if instrument == "power supply":
			print "Utility -> IO Config -> LAN -> LAN Status must be Configured"
		sys.exit("ERROR")

	return tn, id_fields[MODEL]


def connect_verify(instrument, IP, port):
	ping_IP(instrument, IP)
	tn, model = connect_to(instrument, IP, port)
	if instrument == "oscilloscope" and model != "DS1104Z" or \
		 instrument == "power supply" and model != "DP832":
		print model, "is an unknown", instrument, "type."
		sys.exit("ERROR")
	return tn


def command(tn, SCPI):
	tn.write(SCPI)
	response = ""
	while response != "1\n":
		tn.write("*OPC?")                    # operation(s) completed ?
		response = tn.read_until("\n", 1)    # wait max 1s for an answer


def init_oscilloscope(tn):
	# Channel 4 ON
	# BW Limit 20 MHz
	# 10 mV/div
	# POS 0

	# Trig Auto
	# Trig Edge
	# Trig CH4

	tn.write("MEASure:ITEM VAVG, CHANnel4")
	tn.write("*opc?")                     # operation(s) completed ?
	tn.read_until("\n", 1)                # wait max 1s for an answer

	# Run mode ON


def init_power_supply(tn):
	command(tn, "OUTPut CH2, OFF")	          # CH2 OFF
	command(tn, "SOURce2:VOLTage 0")          # CH2 set 0V
	command(tn, "OUTPut:TRACk CH2, OFF")	    # CH2 NOT mirror
	command(tn, "OUTPut:OVP:VALue CH2, 25")   # CH2 OVP limit 25 V
	command(tn, "OUTPut:OVP CH2, ON")         # CH2 OVP on
	command(tn, "OUTPut:OCP:VALue CH2, 3.2")  # CH2 limit 3.2A
	command(tn, "OUTPut:OCP CH2, ON")         # CH2 OCP on
	command(tn, "OUTPut CH2, ON")             # CH2 ON

