# coding: UTF-8
from flask import Flask, request, session, redirect, send_from_directory
import csv, codecs, sys
from global_vars import *
from Tcpserv import Tcpserv
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
	with codecs.open(fname, 'wb', 'gbk') as csvfile:
		writer = csv.writer(csvfile, dialect = 'excel')
		writer.writerow(['设备编号', '温度', '湿度', '照度', '风速', '电磁阀', '时间', '日期'])
		for i in data:
			writer.writerow(i)
	return fname
#--------------------------------

# 主函数
if __name__ == '__main__':
	serv = Tcpserv(clients, db)
	serv.start()
	app.run(port = 8000, debug = True, use_reloader = False)