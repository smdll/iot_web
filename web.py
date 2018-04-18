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
################可以用jsonify
@app.route('/getData', methods = ['GET'])
def jsGetData():
	if 'admin' not in session:
		return ''
	if not clients:
		return ''
	else:
		content = '{'
		for i in clients:
			content += '"' + clients[i].id + '":'
			content += '{'
			content += '"id":"' + clients[i].id + '", '
			content += '"date":"' + clients[i].date + '", '
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
@app.route('/downLog', methods = ['POST'])
def downLog():
	if 'admin' not in session:
		return redirect('/login')
	date = db.getDates()
	fr = request.form.get('from')
	to = request.form.get('to')
	if fr and to in date:
		dataSet = db.getData(fr, to)
		fname = saveFile(dataSet, fr, to)
		return send_from_directory('.', fname, as_attachment = True)
	return send_from_directory('./html', 'download.html')

# JSON发送日期至前端
@app.route('/getDate', methods = ['GET'])
def jsGetDate():
	if 'admin' not in session:
		return ''
	date = db.getDates()
	return jsonify(date)

# 登录页面
@app.route('/login', methods = ['POST'])
def login():
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
	serv = tcpserv(clients, db)
	serv.start()
	app.run(port = 8000, debug = True, use_reloader = False)