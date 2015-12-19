#!/usr/bin/python

import sys
from socket import *
import time
import thread

SERVER_IP = '192.168.1.2'
ECHO_PORT = 50000 + 2
CLIENT_RECV_PORT = 50000 + 4
BUFSIZE = 1024
MAX_TRIES = 50
ENTER_PRESSED = False
PACKETS_RECEIVED = 0;
MIN_THRESHOLD = 10
FOLDER = "Dec19outdoor"
FILE_NAME = FOLDER + "/wifi/wifi-rtt-%.4d.dat"


def main():
	if len(sys.argv) < 2:
		usage()
	if sys.argv[1] == '-c':
		client()
	if sys.argv[1] == '-s':
		server()
	else:
		usage()

def usage():
	print "Server: ./rtt_experiment.py %s [%s]" % ("-s", "port")
	print "Client: ./rtt_experiment.py %s <%s> [%s] [%s]" % ("-c", "distance", "host address", "host port")
	time.sleep(2)
	sys.exit(0)



def server():
	if len(sys.argv) > 2:
		port = int (sys.argv[2])
	else:
		port = ECHO_PORT

	s = socket(AF_INET, SOCK_DGRAM)
	s.bind(('', port))
	print 'Echo server ready'
	while 1:
		data, addr = s.recvfrom(BUFSIZE)
		print 'server received', `data`, 'from', `addr`
		ip, port = addr
		addr = (ip, CLIENT_RECV_PORT)
		s.sendto(data, addr)

	print "Should never get here"
	sys.exit(0)


def client():
	print "Running client"
	if (len(sys.argv) < 3):
		return usage()
	if len(sys.argv) > 4:
		server_port = int(sys.argv[4])
	else:
		server_port = ECHO_PORT
	if len(sys.argv) > 3:
		host = sys.argv[3]
	else:
		host = SERVER_IP
	recv_port = CLIENT_RECV_PORT
	distance = int(sys.argv[2])
	addr = host, server_port
	listen_sock = socket(AF_INET, SOCK_DGRAM)
	listen_sock.bind(('', recv_port))
	sender_sock = socket(AF_INET, SOCK_DGRAM)
	sender_sock.bind(('', 0))
	listen_sock.setblocking(0);
	clientReceiverThread(listen_sock, sender_sock, addr, distance)
	sys.exit(0)

def clientReceiverThread(sock, sender_sock, addr, distance):
	global ENTER_PRESSED
	global PACKETS_RECEIVED
	global FILE_NAME
	total_time = 0
	# thread.start_new_thread(keyboardListener, ())
	thread.start_new_thread(clientSenderThread, (sender_sock, addr))
	data_points = []

	# while (not ENTER_PRESSED) and (PACKETS_RECEIVED < MIN_THRESHOLD):
	while PACKETS_RECEIVED < MIN_THRESHOLD:
		# print "Starting to listen"
		try:
			data, addr = sock.recvfrom(BUFSIZE);
			if (len(data) > 0):
				recv_time = time.time()
				send_time = float(data)
				PACKETS_RECEIVED += 1
				time_taken = recv_time - send_time
				data_points.append(time_taken)
				print "Received Packet in time %f, Total Count = %d" % (time_taken, PACKETS_RECEIVED)
				with open(FILE_NAME % distance, 'a') as f:
					f.write('%.6f\n' % time_taken)
		except:
			pass
	print "Closing listener"
	if (len(data_points) > 0):
		print "Min/Avg/Max ms : %.3f/%.3f/%.3f" % (min(data_points) * 1000, (sum(data_points)/len(data_points))* 1000, max(data_points)* 1000)
	else:
		print "No packets received"
		with open(FILE_NAME % distance, 'a') as f:
					f.write('%.6f\n' % 0)

def clientSenderThread(sock, addr):
	i = 0
	while i < MAX_TRIES and PACKETS_RECEIVED < MIN_THRESHOLD:
		time.sleep(1)
		msg = "%.12f\n" % time.time()
		print "Try number %d" % i
		sock.sendto(msg, addr)
		i+=1

def keyboardListener():
	global ENTER_PRESSED
	inp = raw_input("Press ENTER to stop client server.\n")
	ENTER_PRESSED = True

main()

