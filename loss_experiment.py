#!/usr/bin/python

import sys
from socket import *
import time
import thread
import signal 
SERVER_PORT = 50000
BUFSIZE = 1024
# SINGLE_RUN_TIME = 5
# TIMEOUT = 10
ROUNDS = 3
PACKETS_PER_ROUND = 1000
ENTER_PRESSED = False
SERVER_IP = '192.168.1.2'
FOLDER = "Dec20qncc"
FILE_NAME = FOLDER + "/wifi/wifi-loss-%.4d.dat"
TIMEOUT = 2.0

def main():
	if len(sys.argv) < 3:
		usage()
	if sys.argv[1] == '-c':
		client()
	if sys.argv[1] == '-s':
		server()
	else:
		usage()

def usage():
	print "Server: ./loss_experiment.py %s <%s> <%s> [%s]" % ("-s", "distance", "id", "port")
	print "Client: ./loss_experiment.py %s <%s> [%s] [%s]" % ("-c", "id", "host address", "host port")
	time.sleep(2)
	sys.exit(0)

def sendExp(k, sock, addr, uid):
	print "Running loss experiment round: %d" % k
	for i in range(PACKETS_PER_ROUND):
		msg = "%.4d-%.2d-%2d\n" % (i, k, uid)
		sock.sendto(msg, addr)
	
	time.sleep(2)

def sigint_receiver(n, stack):
	print "Shutting down"
	ENTER_PRESSED = True
	sys.exit(0)

def recvExp(k, sock, data_points, uid, distance):
	global ENTER_PRESSED
	global FILE_NAME
	count = 0
	ENTER_PRESSED = False
	thread.start_new_thread(keyStrokeListener, ())
	while not ENTER_PRESSED:
		empty = True

		try:
			data, addr = sock.recvfrom(BUFSIZE)
			empty = False
		except error:
			pass

		if (not empty):
		 	data = data.split('-')
			round = int(data[1])
			id = int(data[2])
		 	if (round == k) and (id == uid):
				if count == 0:
					print "Received first packet for round %.2d" % k
				count += 1
				if count == PACKETS_PER_ROUND:
					print "Received all packets"
			else:
				print "Received packet for round %d in experiment %d" % (round, id)


	data_points[k] = count
	print "Packets Received : %d/1000" % count
	with open(FILE_NAME % distance, "a") as f:
		loss_percent = 100 - ((count * 100.0)/PACKETS_PER_ROUND)
		f.write("%.2d\t%.2d\t%.2f\n" % (uid, k, loss_percent))

def keyStrokeListener():
	global ENTER_PRESSED
	try:
		raw_input("Press Enter to kill server.\n")
		ENTER_PRESSED = True
	except KeyboardInterrupt:
		return

def server():
	if len(sys.argv) < 4:
		return usage()
	if len(sys.argv) > 4:
		port = int(sys.argv[4])
	else:
		port = SERVER_PORT

	distance = int(sys.argv[2])
	uid = int(sys.argv[3])

	
	data_points = {}

#	signal.signal(signal.SIGINT, sigint_receiver)

	for k in range(1, ROUNDS + 1):
		raw_input("Press Enter to run Server for round %d.\n" % k)
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind(('', port))
		sock.setblocking(0)
		start = time.time()
		print("Receiving Data!") 
		recvExp(k, sock, data_points, uid, distance)
		print ("Round Done in %f seconds" % (time.time() - start))

	print "Results:", data_points
	# with open(FILE_NAME % distance, "a") as f:
	# 	for k, v in data_points.items():
	# 		loss_percent = 100 - ((v * 100.0)/PACKETS_PER_ROUND)
	# 		f.write("%.2d\t%.2d\t%.2f\n" % (uid, k, loss_percent))
	# time.sleep(5)
	sys.exit(0)


def client():
	print "Running client"
	if (len(sys.argv) < 3):
		return usage()
	if len(sys.argv) > 4:
		port = int(sys.argv[4])
	else:
		port = SERVER_PORT
	if (len(sys.argv) > 3):
		host = sys.argv[3]
	else:
		host = SERVER_IP
	uid = int(sys.argv[2])
	addr = host, port

	for k in range(1, ROUNDS + 1):
		sock = socket(AF_INET, SOCK_DGRAM)
		sock.bind(('', 0))
		#sock.settimeout(TIMEOUT)
	#	sock.setblocking(0)
		raw_input("Press Enter to run Client for round %d." % k)
		print("Sending data!") 
		sendExp(k, sock, addr, uid)
		print ("Data Sent")
		try:
			sock.close()
		except error:
			pass
	sys.exit(0)



main()

