# coding: UTF-8
# 全局变量、类定义
from flask import Flask
import sqlite3, ConfigParser
from threading import Lock

# 设备信息类
class Client:
	def __init__(self, valve, **kw):
		self.valve = valve
		self.update(**kw)

	def update(self, **kw):
		for k, v in kw.items():
			setattr(self, k, v)

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

	def getDates(self):
		set = self.cur.execute('SELECT DISTINCT date FROM History ORDER BY date DESC').fetchall()
		result = [i[0] for i in set]
		return result

	def getData(self, fr, to):
		set = self.cur.execute('SELECT * FROM History WHERE date BETWEEN "%s" AND "%s" ORDER BY date ASC'%(fr, to)).fetchall()
		return set

# 初始化全局变量
app = Flask('__main__')
db = DB()
clients = {}
clients_lock = Lock()# 防止线程间冲突
config = ConfigParser.RawConfigParser()
config.read('config.conf')

# 私有变量
maxClients = int(config.get('misc', 'maxClients'))
listen_port = int(config.get('misc', 'listen_port'))
webserv_port = int(config.get('misc', 'webserv_port'))

app.secret_key = config.get('security', 'session_key')
username = config.get('security', 'username')
password = config.get('security', 'password')
