# coding: UTF-8
# 此脚本用于清除所有导出数据以及重置数据库，请小心使用
def init():
	import MySQLdb

	conn = MySQLdb.connect('localhost', 'root', '', 'iot')
	cur = conn.cursor()

	cur.execute('DROP TABLE IF EXISTS History')
	cur.execute('DROP TABLE IF EXISTS Valve')
	cur.execute('CREATE TABLE History(id TINYTEXT , temp TINYTEXT , humid TINYTEXT , lux TINYTEXT , spd TINYTEXT , volt TINYTEXT , time TINYTEXT , date TINYTEXT )')
	cur.execute('CREATE TABLE Valve(id TINYINT PRIMARY KEY, control TINYTEXT , stat TINYTEXT )')
	conn.commit()

if __name__ == '__main__':
	init()
