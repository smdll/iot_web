# coding: UTF-8
from flask import *
import csv, codecs, sys
from global_vars import *
from tcpserv import tcpserv
reload(sys)
sys.setdefaultencoding('utf-8')

#------------页面部分------------
# 根页面
@app.route('/')
def home():
	if 'admin' not in session:
		return redirect('/login')
	return send_from_directory('./html', 'index.html')

# JSON发送数据至前端
@app.route('/getData', methods = ['GET'])
def jsGetData():
	if 'admin' not in session:
		return ''
	if not clients:
		return ''
	else:
		content = '{'
		for i in clients:
			content += '"' + i + '":'
			content += '{'
			content += '"id":"' + clients[i].id + '", '
			content += '"date":"' + clients[i].date + '  ' + clients[i].time + '", '
			content += '"temp":"' + clients[i].temp + '", '
			content += '"humid":"' + clients[i].humid + '", '
			content += '"lux":"' + clients[i].lux + '", '
			content += '"spd":"' + clients[i].spd + '", '
			content += '"valve":"' + clients[i].valve + '"},'
		content = content[:-1] + '}'
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
# POST与GET事件共存
@app.route('/downLog', methods = ['POST', 'GET'])
def downLog():
	def generate(data):
		header = ['设备编号', '温度', '湿度', '照度', '风速', '电磁阀', '时间', '日期']
		text = ','.join(header) + '\n'
		for i in data:
			text += ','.join(i) + '\n'
		text = text.decode('utf-8').encode('gbk')
		yield text

	if 'admin' not in session:
		return redirect('/login')
	date = db.getDates()
	fr = min(request.form.get('from'), request.form.get('to'))
	to = max(request.form.get('from'), request.form.get('to'))
	if fr and to in date:
		dataSet = db.getData(fr, to)
		rep = Response(generate(dataSet), mimetype = 'text/csv')
		rep.headers['Content-Disposition'] = 'filename=%s'%'%s_%s.csv'%(fr, to)
		return rep
	return send_from_directory('./html', 'download.html')

# JSON发送日期至前端
@app.route('/getDate', methods = ['GET'])
def jsGetDate():
	if 'admin' not in session:
		return ''
	date = db.getDates()
	return jsonify(date)

# 登录页面
# POST与GET事件共存
@app.route('/login', methods = ['POST', 'GET'])
def login():
	if 'admin' in session:
		return redirect('/')
	if request.form.get('username') == username and request.form.get('password') == password:
		session[request.form.get('username')] = True
		return redirect('/')
	return send_from_directory('./html', 'login.html')

# 登出页面
@app.route('/logout')
def logout():
	if 'admin' in session:
		session.pop('admin')
	return redirect('/login')
#--------------------------------

# 主函数
if __name__ == '__main__':
	serv = tcpserv(clients, db)
	serv.start()
	app.run(port = webserv_port, debug = True, use_reloader = False)