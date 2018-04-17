# coding: UTF-8
# 全局变量、类定义
from flask import Flask
import sqlite3

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
app = Flask(__name__)
db = DB()
clients = {}
maxClients = 5

# 私有变量，部署后修改
app.secret_key = 'try me' # 修改成私有字符串
username = 'admin'
password = '123456'