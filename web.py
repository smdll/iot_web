# coding: UTF-8
from flask import *
import csv, codecs, sys, json, sqlite3, ConfigParser
reload(sys)
sys.setdefaultencoding('utf-8')

# 数据库类
class DB:
	def __init__(self):
		self.conn = sqlite3.connect('history.db', check_same_thread = False)
		self.cur = self.conn.cursor()

	def getDates(self):
		set = self.cur.execute('SELECT DISTINCT date FROM History ORDER BY date DESC').fetchall()
		result = [i[0] for i in set]
		return result

	def getData(self, fr, to):
		set = self.cur.execute('SELECT * FROM History WHERE date BETWEEN "%s" AND "%s" ORDER BY date ASC'%(fr, to)).fetchall()
		return set
	
	def getNewest(self):
		set = self.cur.execute('SELECT * FROM History ORDER BY id').fetchall()
		return set

	def setValve(self, id, valve):
		self.cur.execute('UPDATE Valve SET control="%s", stat="%s" WHERE id=%s'%(valve, valve, id))
		self.conn.commit()

	def getValve(self, id):
		stat = self.cur.execute('SELECT stat FROM Valve WHERE id=%s'%id).fetchone()[0]
		return stat

	def getCont(self, id):
		stat = self.cur.execute('SELECT control FROM Valve WHERE id=%s'%id).fetchone()[0]
		return stat

app = Flask('__main__')
db = DB()

config = ConfigParser.RawConfigParser()
config.read('config.conf')

is_debug = config.get('misc', 'debug')

app.secret_key = config.get('security', 'session_key')
username = config.get('security', 'username')
password = config.get('security', 'password')

# 登录页面
# POST与GET事件共存
@app.route('/login', methods = ['POST', 'GET'])
def login():
	if username in session:
		return redirect('/')
	uname = str(request.form.get('username'))
	upass = str(request.form.get('password'))
	if uname == username and upass == password:
		session[request.form.get('username')] = True
		return redirect('/')
	return send_from_directory('./html', 'login.html')

# 登出页面
@app.route('/logout')
def logout():
	if username in session:
		session.pop(username)
	return redirect('/login')

# 根页面
@app.route('/')
def home():
	if username not in session:
		return redirect('/login')
	return send_from_directory('./html', 'index.html')


# 下载记录
# POST与GET事件共存
@app.route('/downLog', methods = ['POST', 'GET'])
def downLog():
	def generate(data):
		header = ['设备编号', '温度', '湿度', '照度', '风速', '电压', '时间', '日期']
		text = ','.join(header) + '\n'
		for i in data:
			text += ','.join(i) + '\n'
		text = text.decode('utf-8').encode('gbk')
		yield text

	if username not in session:
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

# 电磁阀
# POST事件用于根页面电磁阀状态更改的数据处理
@app.route('/valveHandle', methods = ['POST'])
def valveHandle():
	if username not in session:
		return redirect('/login')
	data = request.get_data()
	dict = json.loads(data)
	id = str(dict['id'])
	db.setValve(id, str(dict['valve']))
	return ''

# JSON发送数据至前端
@app.route('/getData', methods = ['GET'])
def jsGetData():
	if username not in session:
		return ''
	content = ''
	clients = db.getNewest()
	if clients:
		content += '{'
		for i in clients:
			content += '"' + i[0] + '":'
			content += '{'
			content += '"id":"' + i[0] + '", '
			content += '"date":"' + i[7] + '  ' + i[6] + '", '
			content += '"temp":"' + i[1] + '", '
			content += '"humid":"' + i[2] + '", '
			content += '"lux":"' + i[3] + '", '
			content += '"spd":"' + i[4] + '", '
			content += '"volt":"' + i[5] + '", '
			content += '"cont":"' + db.getCont(i[0]) + '", '
			content += '"valve":"' + db.getValve(i[0]) + '"},'
		content = content[:-1] + '}'
	return content

# JSON发送日期至前端
@app.route('/getDate', methods = ['GET'])
def jsGetDate():
	if username not in session:
		return ''
	date = db.getDates()
	return jsonify(date)

# 主函数
if __name__ == '__main__':
	app.run(debug = is_debug, use_reloader = False)

'''
TODO:
	图表
'''