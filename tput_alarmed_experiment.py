#!/usr/bin/python


# import bluetooth
import time
# import threading
import multiprocessing
import sys
import timeit
import signal
import socket
import os.path

SERVER_ADDR = '192.168.1.2'
SERVER_PORT = 50000 + 6
FILE_SIZE = 20 * 1024 * 1024
BUFSIZE = 10 * 1024
ENTER_PRESSED = False
CONNECTIONS = 0;
MIN_THRESHOLD = 5
TIME_THREASHOLD = 2
START_TIME = 0
BYTES_RECEIVED = 0
MAX_TRIES = 50
TIMEOUT = 10.0
END_TIME = 0
DISTANCE = 0
FOLDER = "Dec20qncc"
FILE_NAME = FOLDER + "/wifi/wifi-tput-%.4d.dat"
#SOCK = 0
# data_points = []

def main():
	if len(sys.argv) < 2:
		usage()
	if sys.argv[1] == '-c':
		client()
	elif sys.argv[1] == '-s':
		server()
	else:
		usage()

def usage():
	print "Server: ./tput_alarmed_experiment.py %s <%s> [%s]" % ("-s", "distance", "port")
	print "Client: ./tput_alarmed_experiment.py %s [%s] [%s]" % ("-c", "host address", "host port")
	# time.sleep(2)
	sys.exit(0)

def alarm_receiver(n, stack):
	global DISTANCE
	global FILE_NAME
#	global SOCK
	END_TIME = timeit.default_timer()
	time_taken = END_TIME - START_TIME
	
	print "Received Bytes: %d in time %.3f\n" % (BYTES_RECEIVED, time_taken)
	print "Throughput KB/s =  %.3f" % (BYTES_RECEIVED / (time_taken * 1024))
	
	if (BYTES_RECEIVED >= FILE_SIZE):
		print "Received complete File, you should increase the file size..."
	
	with open(FILE_NAME % DISTANCE, "a") as f:
			f.write("%d\t%.6f\n" % (BYTES_RECEIVED, time_taken))
#	SOCK.shutdown(socket.SHUT_RD)
#	SOCK.close()
	sys.exit(0)

def receieverThread(sock, distance):
	global START_TIME
	global BYTES_RECEIVED
	global DISTANCE
#	global SOCK
#	SOCK = sock
	DISTANCE = distance	
	BYTES_RECEIVED = 0

#	sock.setblocking(0)
	signal.signal(signal.SIGALRM, alarm_receiver)
	START_TIME = timeit.default_timer()
	signal.alarm(TIME_THREASHOLD)
	while True:
		#try:
			d = sock.recv(FILE_SIZE)
			if (d == 0):
				print "connection closed early"
			BYTES_RECEIVED += len(d)
		#except socket.error:
		#	pass
	
	


def server():
	global DISTANCE
	global FILE_NAME

	if (len(sys.argv) < 3):
		return usage()
	if (len(sys.argv) > 3):
		port = sys.argv[3]
	else:
		port = SERVER_PORT

	distance = int(sys.argv[2])
	DISTANCE = distance

	if (not os.path.isfile(FILE_NAME % DISTANCE)):
		with open(FILE_NAME % DISTANCE, "a") as f:
				f.write("%s\t%s\n" % ("Data (bytes)", "Time (ms)"))
	server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_sock.bind(('', port))
	server_sock.listen(1)
	while True:
		client_sock, addr = server_sock.accept()
		print "Got Connection from ", addr
		p = multiprocessing.Process(target = receieverThread, args = (client_sock, distance, ))
		p.start()
		p.join()
		try:
			client_sock.shutdown(socket.SHUT_RD)
			client_sock.close()
		except:
			pass


def client():
	global CONNECTIONS
	global MIN_THRESHOLD
	global MAX_TRIES
	tries = 0
	if len(sys.argv) > 3:
		port = int(sys.argv[3])
	else:
		port = SERVER_PORT
	if len(sys.argv) > 2:
		host = sys.argv[2]
	else:
		host = SERVER_ADDR

	addr = (host, port)
	msg = '0' * FILE_SIZE

	while CONNECTIONS < MIN_THRESHOLD and tries < MAX_TRIES:
		print "Trying, attempt %d" % tries
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.settimeout(TIMEOUT)
		try:
			sock.connect(addr)
			print "Connected, Sending..."
			try:
				sock.sendall(msg)
				print "Done sending."
			except:
				print "Could not send complete file"
			CONNECTIONS += 1
		except:
			print "No Connection Timeout"
		try:
			sock.close()
		except:
			pass
		tries += 1
		time.sleep(1)

main()
