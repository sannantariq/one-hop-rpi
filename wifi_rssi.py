#!/usr/bin/python

import os
import sys
import time

FOLDER = "Dec20offices"
FILE_NAME = FOLDER + "/wifi/wifi-rssi-%.4d.dat"
# ADDR = '98:4F:EE:03:6E:18'
RUNS = 5
THRESH = 5

def main():
	if len(sys.argv) < 2:
		usage()
	else:
		rssi()

def usage():
	print "Usage: ./wifi_rssi.py <%s>" % 'distance'
	sys.exit(0)

def rssi():
	global RUNS
	global THRESH
	global ADDR
	tries = 0
	correct = 0
	distance = int(sys.argv[1])

	with open(FILE_NAME % distance, 'a') as f:
		pass

	while (tries < RUNS) and (correct < THRESH):
		with os.popen('wpa_cli scan') as f:
			pass
		time.sleep(1)
		with os.popen('wpa_cli scan_results | grep "EdiNet"')  as f:
			raw = f.readlines()

		raw = [line.strip().split() for line in raw]
		vals = [int(line[2]) for line in raw]
		print vals
		if len(vals) < 1 or ((vals[0] == 0) and all(vals)):
			print "Could not find another beacon"
		else:
			val = min(vals)
			if (val < 0):
				with open(FILE_NAME % distance, 'a') as f:
					f.write('%.3d\n' % val)
				print "RSSI = %d" % val
				correct += 1
			else:
				print "No valid value found"
		tries += 1

main()




