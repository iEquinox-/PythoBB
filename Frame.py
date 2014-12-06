class Main:
	def __init__(self):
		import sqlite3,os,re,json
		self.modules = [os,sqlite3,re,json]
		self.dir = "/home/equinox/pythobb/pythobb/" # Dir of PythoBB
		self.db = self.connect()

	def connect(self): # Connect to DB
		d = self.modules[1].connect(self.dir+"database.db")
		c = d.cursor()
		return [d,c]

	def execute(self,q,s=False):
		if q:
			try:
				res = self.db[1].execute(q)
				if s:
					self.db[0].commit()
					return [c for c in res]
				else:
					return [c for c in res]
			except Exception as e:
				return str(e)
		else:
			return

class User:
	def __init__(self):
		m = Main()

	def viewuser(self,username):
		try:
			d = [c for c in Main().execute(
					q="SELECT * FROM pythobb_users WHERE username='%s'" % (
						username
						),
					s=False
					)
				]
			if len(d) == 0:
				return "No such user."
			else:
				return {"username":d[0][0],"registered":d[0][5],"group":d[0][6],"uid":d[0][-1],"avatar":d[0][4]}
		except Exception as e:
			return str("".join(e))

	def create(self,vars):
		import time
		if len(vars) >= 9:
			if vars["username"] == "":
				return "Username cannot be null."
			if vars["password"]=="":
				return "Password cannot be null."
			if vars["email"] == "":
				return "Email cannot be null."
			def salt():
				import string,random
				n = ""
				for x in range(0,5):
					n += random.choice(
						list(
							string.ascii_letters+"+_)(*&^%$#@!"
						)
					)
				return n
			def uid():
				return int(len([c for c in Main().execute(q="SELECT * FROM pythobb_users",s=False)])+1)
			try:
				Main().execute(
					q="INSERT INTO pythobb_users VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
						vars["username"],
						vars["password"],
						salt(),
						vars["email"],
						vars["avatar"],
						str(time.time()),str(time.time()),
						vars["usertitle"],
						vars["group"],
						str(uid())
						),
					s = True
					)
				return True
			except Exception as e:
				return False,str(e)
		else:
			return "Variable \"vars\" (DictType) too short."

class Pages:
	def __init__(self):
		from django.http import HttpResponse
		self.resp = HttpResponse
		self.temp = {"Index":self.getTemplate("header")+"<body><div class='title'>Welcome to PythoBB.</div></body>"}
			
	def getTemplate(self, x, vars=None):
		import re,json
		f = {
			"forumtitle":"PythoBB",
			"forumurl":"http://127.0.0.1:8000/"
			}
		if vars != None:
			f = {
				"forumtitle":"PythoBB",
				"forumurl":"http://127.0.0.1:8000/",
				"avatar":"<img src='%s'/ class='profava'>" % (vars["avatar"]),
				"username":vars["username"]
				}
		y = open(Main().dir + "templates/%s.ptmp" % (x),"r").read()
		for c in re.findall("\{\[(.*?)\]\}",y):
			y = y.replace("{[%s]}"%(c),f[c])
		return y

	def Index(self, request):
		return self.resp(self.temp["Index"])

	def Profile(self, request, username):
		f = User().viewuser(username)
		# f["username"]+" "+f["registered"]+" "+f["group"]+" "+f["uid"]
		page = self.getTemplate("header")+self.getTemplate("profile",vars=f)
		return self.resp(page)
