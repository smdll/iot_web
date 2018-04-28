# coding: UTF-8
# TCP服务器类
import socket, threading, traceback, sqlite3, ConfigParser
from time import localtime, strftime

# 数据库类
class DB:
	def __init__(self):
		self.conn = sqlite3.connect('history.db', check_same_thread = False)
		self.cur = self.conn.cursor()

	def addData(self, **kw):
		sql = ("INSERT INTO History(%s) VALUES (%s)"%
				(", ".join(kw.keys()),
				 ", ".join("?" for _v in kw.values())))
		self.cur.execute(sql, kw.values())
		self.conn.commit()

	def setValve(self, id, valve):
		self.cur.execute('INSERT OR IGNORE INTO Valve(id, control, stat) VALUES(%s, "%s", "%s")'%(id, valve, valve))##########插入冗余数据问题
		self.conn.commit()

	def getValve(self, id):
		stat = self.cur.execute('SELECT control FROM Valve WHERE id=%s'%id).fetchone()[0]
		return stat

db = DB()
config = ConfigParser.RawConfigParser()
config.read('config.conf')

maxClients = int(config.get('misc', 'maxClients'))
ip_addr = config.get('misc', 'ip_addr')
listen_port = int(config.get('misc', 'listen_port'))

# Socket监听线程
def recvThd():
	recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	recv.bind((ip_addr, listen_port))
	recv.listen(maxClients)
	while True:
		sock, addr = recv.accept()
		t = threading.Thread(target = post, args=(sock, addr))
		t.start()

# 提交数据
# 建立TCP服务器和多线程来处理设备提交的新数据，提交完后返回电磁阀状态
# rx:id,temp,humid,lux,spd,valve
# tx:valve(new)
def post(sock, addr):
	print '%s:%s established'%addr
	sock.settimeout(20) # 设置超时20秒
	while True:
		try:
			rawdata = sock.recv(1024)
			if not isValid(rawdata):
				break
			valve, data = parse(rawdata)
			id = data['id']
			db.addData(**data)
			db.setValve(id, valve)
			#!7
			sock.send('!' + db.getValve(id))
		except:
			traceback.print_exc()
			break
	print '%s:%s closed'%addr
	sock.close()

# 数据解析
def parse(input):
	data = input.split(',')
	valve = data[6]
	data = {'id':  data[0],
			'temp': data[1],
			'humid': data[2],
			'lux': data[3],
			'spd': data[4],
			'volt': data[5]}
	data['date'] = strftime('%Y-%m-%d', localtime())
	data['time'] = strftime('%H:%M:%S', localtime())
	return valve, data

# 检查数据是否合法
def isValid(input):
	data = input.split(',')
	if len(data) == 7:
		return True
	return False

if __name__ == '__main__':
	t = threading.Thread(target = recvThd)
	print 'thread started'
	t.start()
