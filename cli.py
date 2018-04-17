import socket, sys, time
from random import *

id = raw_input()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 1234))

while True:
	try:
		valve = '7'
		s.send('%s,%d,%d,%d,%d,%s'%(id, randint(15, 30), randint(30, 60), randint(1000, 100000), randint(0, 5), valve))
		valve = s.recv(1024)
		print valve
		time.sleep(5)
	except KeyboardInterrupt, Exception:
		s.send('bye')
		s.close()
		break