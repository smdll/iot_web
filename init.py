# coding: UTF-8
# 此脚本用于清除所有导出数据以及重置数据库，请小心使用

def init():
	import sqlite3, os, platform

	sysstr = platform.system()
	if sysstr == 'Windows':
		if os.path.exists('history.db'):
			os.system('del history.db')
		os.system('del *.csv')
	elif sysstr == 'Linux':
		if os.path.exists('history.db'):
			os.system('rm -f history.db')
		os.system('rm -f *.csv')
	else:
		return

	conn = sqlite3.connect('history.db')
	cur = conn.cursor()

	cur.execute('CREATE TABLE History(id TEXT, temp TEXT, humid TEXT, lux TEXT, spd TEXT, valve TEXT, time TEXT, date TEXT)')
	conn.commit()

if __name__ == '__main__':
	init()
