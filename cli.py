import socket, sys, time
from random import *

id = raw_input()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect(('47.106.9.49', 1234))
s.connect(('127.0.0.1', 1234))

while True:
	try:
		valve = '7'
		s.send('%s,%d,%d,%d,%d,%.1f,%s'%(id, randint(15, 30), randint(30, 60), randint(1000, 100000), randint(0, 5), uniform(11.2, 16.8), valve))
		valve = s.recv(1024)
		print valve
		time.sleep(5)
	except KeyboardInterrupt, Exception:
		s.close()
		break