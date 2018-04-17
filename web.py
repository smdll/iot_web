# coding: UTF-8
from flask import Flask, request, session, redirect, send_from_directory
from time import localtime, strftime
import csv, codecs, sys, socket, threading
from global_vars import *
reload(sys)
sys.setdefaultencoding('utf-8')

#------------页面部分------------
# 根页面
@app.route('/')
def home():
	if 'admin' not in session:
		return redirect('/login')
	content = u'''
				<head><meta http-equiv="refresh" content="10"></head>
				<input type="button" value="注销" onclick="window.location.href='/logout'"/>
				<input type="button" value="导出数据" onclick="window.location.href='/getLog'"/><br />
			'''
	if not clients:####################clients无法全局
		content += u'<hl>无设备</hl>'
	else:
		for i in clients:
			content += u'<p><form action="/valveHandle" method="post">设备编号: ' + i + '<br />'
			content += u'最后更新：' + clients[i].date + '  ' + clients[i].time + '<br />'
			content += u'温度: ' + clients[i].temp + u'°C<br />'
			content += u'湿度: ' + clients[i].humid + '%<br />'
			content += u'照度: ' + clients[i].lux + 'lux<br />'
			content += u'风速: ' + clients[i].spd + 'm/s<br />'
			content += u'<label>电磁阀状态:</label>'

			stat = getValveStat(clients[i].valve)
			content += '<input type="hidden" name="id" value="' + i + '">'
			content += '<label><input type="checkbox" value="0" name="cli' + i + '_1"' + stat[0] + '>3</label>'
			content += '<label><input type="checkbox" value="1" name="cli' + i + '_2"' + stat[1] + '>2</label>'
			content += '<label><input type="checkbox" value="2" name="cli' + i + '_3"' + stat[2] + '>1</label>'
			content += u'<label><input type="submit" value="设置">'
			content += '</form></p>'
	return content

# 电磁阀
# POST事件用于根页面电磁阀状态更改的数据处理
@app.route('/valveHandle', methods = ['POST'])
def valveHandle():
	if 'admin' not in session:
		return redirect('/login')
	id = request.form.get('id')
	if id in clients:
		valve_stat = 0
		for i in request.form:
			if i == 'id':
				continue
			valve_stat += pow(2, int(request.form.get(i)))
		clients[id].valve = str(valve_stat)
		return redirect('/')

	return ''
'''
# 提交新数据
# data: /post?id=1&temp=20&humid=50&lux=1000&spd=3&valve=5
@app.route('/post', methods = ['GET'])
def post():
	id = request.args['id']
	temp = request.args['temp']
	humid = request.args['humid']
	lux = request.args['lux']
	spd = request.args['spd']
	valve = request.args['valve']

	date = strftime("%Y-%m-%d", localtime())
	time = strftime("%H:%M:%S", localtime())
	if not clients.has_key(id):
		clients[id] = Client(temp, humid, lux, spd, valve, time, date)
	else:
		clients[id].update(temp, humid, lux, spd, valve, time, date)

	db.addData(id, temp, humid, lux, spd, valve, time, date)
	return ''
'''
# 下载记录
@app.route('/getLog', methods = ['POST', 'GET'])
def getLog():
	if 'admin' not in session:
		return redirect('/login')
	date = db.getDates()
	fr = request.form.get('from')
	to = request.form.get('to')
	if fr and to in date:
		dataSet = db.getData(fr, to)
		fname = saveFile(dataSet, fr, to)
		return send_from_directory('.', fname, as_attachment = True)

	form = u'<form method="post"><p>从：<select name="from">'
	for i in date:
		form += u'<option value ="%s">%s</option>'%(i, i)
	form += u'</select><p>到：<select name="to">'
	for i in date:
		form += u'<option value ="%s">%s</option>'%(i, i)
	form += u'</select><p><input type=submit value="下载"></form>'
	return form

# 登录页面
@app.route('/login', methods = ['POST', 'GET'])
def login():
	if request.form.get('username') == username and request.form.get('password') == password:
		session[request.form.get('username')] = True
		return redirect('/')
	return u'''
			<form method="post">
				<p>用户名：<input type=text name="username">
				<p>密码：<input type=password name="password">
				<p><input type=submit value="登录">
			</form>'''

# 登出页面
@app.route('/logout')
def logout():
	if 'admin' in session:
		session.pop('admin')
	return redirect('/login')
#--------------------------------


#----------各种处理函数----------
# 提交数据
# TODO: 建立TCP服务器和多线程来处理设备提交的新数据，提交完后返回电磁阀状态
# id=1,temp=20,humid=50,lux=1000,spd=3,valve=5
def post(sock, addr):
	print '%s:%s established'%addr
	while True:
		rawdata = sock.recv(1024)
		if rawdata == 'bye':
			break
		data = rawdata.split(',')
		valve = data[5]
		data = {"id":  data[0],
				"temp": data[1],
				"humid": data[2],
				"lux": data[3],
				"spd": data[4]}
		data["date"] = strftime("%Y-%m-%d", localtime())
		data["time"] = strftime("%H:%M:%S", localtime())

		#import pdb; pdb.set_trace()
		id = data["id"]
		if not clients.has_key(id):
			clients[id] = Client(valve, **data)
		else:
			clients[id].update(**data)
		sock.send(clients[id].valve)
		db.addData(valve = clients[id].valve, **data)
	print '%s:%s closed'%addr
	sock.close()

# 电磁阀状态
def getValveStat(input):
	input = int(input)
	result = []
	for i in range(3):
		if input & 1 == 1:
			result.append(' checked="true"')
		else:
			result.append('')
		input = input >> 1
	return result

# 保存文件
def saveFile(data, fr, to):
	fname = '%s_%s.csv'%(fr, to)
	with codecs.open(fname, 'wb', "gbk") as csvfile:
		writer = csv.writer(csvfile, dialect = 'excel')
		writer.writerow(['设备编号', '温度', '湿度', '照度', '风速', '电磁阀', '时间', '日期'])
		for i in data:
			writer.writerow(i)
	return fname

# socket独立线程
def recvThd():
	recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	recv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	recv.bind(('localhost', 1234))
	recv.listen(maxClients)
	while True:
		sock, addr = recv.accept()
		t = threading.Thread(target = post, args=(sock, addr))
		t.start()
#--------------------------------

# 主函数
if __name__ == '__main__':
	t = threading.Thread(target = recvThd)
	t.setDaemon(True)
	t.start()
	app.run(port = 8000, debug = True, use_reloader = False)