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
    response = ""
    while response != "1\n":
        tn.write("*OPC?")  # operation(s) completed ?
        response = tn.read_until("\n", 1)  # wait max 3s for an answer

    tn.write(SCPI)


def init_oscilloscope(tn):
    # General settings
    command(tn, "RUN")                      # Run mode ON

    # Channel 1 settings
    command(tn, "CHANnel1:PROBe 10")

    command(tn, "CHANnel1:BWLimit 20M")     # BW Limit 20 MHz
    command(tn, "CHANnel1:COUPling DC")
    command(tn, "CHANnel1:SCALe 0.01")      # 10 mV/div
    command(tn, "CHANnel1:OFFSet 0")        # If the trace is out of range, the Vavg can not be calculated
    command(tn, "CHANnel1:DISPlay ON")

    # Timebase settings
    command(tn, "TIMebase:MAIN:SCALe 0.0001")

    # Trigger settings
    command(tn, "TRIGger:SWEep AUTO")       # Trig Auto
    command(tn, "TRIGger:EDGe:SOURce CHANnel1")
    command(tn, "TRIGger:EDGe:LEVel 0")

    # Acquisition settings

    # Measurement settings
    # command(tn, "MEASure:STATistic:RESet")


def init_power_supply(tn):
    command(tn, "OUTPut:TRACk CH1, OFF")        # CH2 NOT mirror

    command(tn, "SOURce1:VOLTage 0")            # CH2 set 0V
    command(tn, "SOURce1:CURRent 3")            # CH2 set 3A

    command(tn, "OUTPut:OVP:VALue CH1, 25")     # CH2 OVP limit 25 V
    command(tn, "OUTPut:OVP CH1, ON")           # CH2 OVP on
    command(tn, "OUTPut:OCP:VALue CH1, 3.2")    # CH2 limit 3.2A
    command(tn, "OUTPut:OCP CH1, ON")           # CH2 OCP on
    command(tn, "OUTPut CH1, ON")               # CH2 ON
