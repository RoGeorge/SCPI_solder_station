__author__ = 'RoGeorge'
#
# TODO: Port for Linux
# TODO: Add a preheat thermocouple test
# TODO: Add auto calibrate for PID
# TODO: Add command line parameters for instruments IPs
# TODO: Add GUI
# TODO: Create versioned executable distributions
#
from time import *
from sys import *
import os
from msvcrt import getch, kbhit

from functions import connect_verify, init_oscilloscope, init_power_supply, command

# Update the next lines for your own default settings:
tSet = 250                      # Required temperature set in Celsius
tAmb = 25

# approx. 200*C at 7V without thermal load
# infinite wait, for delta 1 Volt -> delta 20 Celsius
# 37 seconds at 24V, from -2.82 mV to 20.9 mV (at 40uV/*C -> approx. 16*C/s for 24V)
# measured tip temperature = 178*C at V thermocouple = 8.2mV (205*C) -> tip is 27*C lower
# kP = 24.0 / 16.0 / 1000

# Ziegler-Nichols method: Set kI and kD to 0.
# Find kUltimate by increasing kP until the system oscillates.
# pU is the oscillation period. Choose coefficients as follows:
# +----------------------------------------------+
# | Control Type |   kP    |    kI     |   kD    |
# +--------------+---------+-----------+---------+
# | P            | 0.50*kU |     0     |    0    |
# | PI           | 0.45*kU | 1.2*kP/pU |    0    |
# | PID          | 0.60*kU | 2.0*kP/pU | kP*pU/8 |
# +--------------+---------+-----------+---------+

# kU = 200 * 24.0 / 16.0 / 1000, fOsc=1...2 Hz
kU = 200 * 24.0 / 16.0 / 1000
pU = 1.5

kP = 0.6 * kU
kI = 0              # 2.0 * kP / pU
kD = 0              # kP * pU / 8.0

IP_DS1104Z = "192.168.1.3"      # Oscilloscope LAN IP address
IP_DP832 = "192.168.1.4"        # Power Source LAN IP address

vOutMin = float(0)              # Minimum voltage for the soldering iron
vOutMax = float(24)             # Maximum voltage supported by the soldering iron

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
print script_name, 'usage:'
print '   - press UP arrow key to increase the temperature'
print '   - press DOWN arrow key to decrease the temperature'
print '   - press ESC key to stop the heater and exit'
print
print 'Initializing...'

# Connect and check instruments
tn_oscilloscope = connect_verify("oscilloscope", IP_DS1104Z, port)
tn_power_source = connect_verify("power supply", IP_DP832, port)

# Initialize instruments
init_oscilloscope(tn_oscilloscope)
init_power_supply(tn_power_source)

print "Preheating..."
# Check preheat
vOut = 0
command(tn_power_source, "SOURce1:VOLTage " + str(vOut))

# Temperature control loop
key = 0
previousTime = time()
vBias = 7.0 + (tSet - 200) / 20
iErr = 0.0
dErr = 0.0
pErrPrevious = 0.0
while True:
    # Read thermocouple
    tn_oscilloscope.write("MEASure:ITEM? VAVG, CHANnel1")
    buff = tn_oscilloscope.read_until("\n", small_wait)

    currentTime = time()
    deltaTime = (currentTime - previousTime) * 1000     # control loop duration in ms
    if deltaTime == 0:
        # Prevent division by zero err
        deltaTime = 1

    previousTime = currentTime

    if len(buff) > 0:
        # print 'buff =', buff[:-1]
        if ("0" <= buff[0] <= "9") or buff[0] == "-":
            # Convert thermocouple voltage readings to *C
            t = tAmb + abs(float(buff[:-1])) / 0.000040
            # print 'T read =', t, '*C'
        else:
            print 'Read ERROR!', buff
            # Will assume the current temperature is slightly higher then requested
            t = tSet + 1
    else:
        print 'Empty buffer ERROR!', buff
        # Will assume the current temperature is slightly higher then requested

    # Compute next output voltage to compensate for any temperature error
    pErr = tSet - t
    iErr += pErr * deltaTime
    dErr = (pErr - pErrPrevious) / deltaTime
    pErrPrevious = pErr

    vOut = vBias + kP * pErr + kI * iErr + kD * dErr
    if vOut < 0:
        vOut = 0
    if vOut > vOutMax:
        vOut = vOutMax

    # read pressed key without waiting http://code.activestate.com/recipes/197140/
    if kbhit():                         # Key pressed?
        key = ord(getch())              # get first byte of keyscan code
        if key == 0 or key == 224:      # is it a function key? (0 for F1..n, 224 for arrows & others)
            key = ord(getch())          # read second byte of key scan code
    else:
        key = 0

    if key == 27:   # exit if ESC pressed
        break

    if key == 72:
        tSet += 5
    if key == 80:
        tSet -= 5

    if tSet > 400:
        tSet = 400
    if tSet < 100:
        tSet = 100

    vGraph = '|.........................|'
    vIndex = 1 + int(0.5 + vOut)
    tGraph = '|..............................|'
    if t > 100:
        tIndex = 1 + int((t - 100)/10)
    else:
        tIndex = 1
    # display
    print vGraph[:vIndex] + 'v' + vGraph[vIndex + 1:], \
          tSet, '*C   t=', \
          tGraph[:tIndex] + 't' + tGraph[tIndex + 1:], int(t), '*C'

    # Set new voltage
    command(tn_power_source, "SOURce1:VOLTage " + "{0:.3f}".format(vOut))
    # Loop until a stop request encountered

# power off
command(tn_power_source, "OUTPut CH1, OFF")

# Close telnet sessions and exit
tn_oscilloscope.close()
tn_power_source.close()
print "Power OFF. Normal exit. Bye!"
