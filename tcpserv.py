# coding: UTF-8
# TCP服务器类
import socket, threading
from global_vars import *
from time import localtime, strftime
class tcpserv:
	def __init__(self):
		self.t = threading.Thread(target = self.recvThd)
		self.t.setDaemon(True)

	def start(self):
		self.t.start()

	# Socket监听线程
	def recvThd(self):
		recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		recv.bind(('localhost', listen_port))
		recv.listen(maxClients)
		while True:
			sock, addr = recv.accept()
			t = threading.Thread(target = self.post, args=(sock, addr))
			t.start()

	# 提交数据
	# 建立TCP服务器和多线程来处理设备提交的新数据，提交完后返回电磁阀状态
	# rx:id,temp,humid,lux,spd,valve
	# tx:valve(new)
	def post(self, sock, addr):
		print '%s:%s established'%addr
		while True:
			try:
				rawdata = sock.recv(1024)
				valve, data = self.parse(rawdata)
				id = data['id']
				if clients_lock.acquire():
					if not clients.has_key(id):
						clients[id] = Client(valve, **data)
					else:
						clients[id].update(**data)
					db.addData(valve = clients[id].valve, **data)
					valve = clients[id].valve
					clients_lock.release()
					sock.send(valve)
			except:
				break
		print '%s:%s closed'%addr
		sock.close()

	# 数据解析
	def parse(self, input):
		data = input.split(',')
		valve = data[5]
		data = {'id':  data[0],
				'temp': data[1],
				'humid': data[2],
				'lux': data[3],
				'spd': data[4]}
		data['date'] = strftime('%Y-%m-%d', localtime())
		data['time'] = strftime('%H:%M:%S', localtime())
		return valve, data