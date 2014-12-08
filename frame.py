class Main:
	def __init__(self):
		import sqlite3,os,re,json
		self.modules = [os,sqlite3,re,json]
		self.forum = "PythoBB"
		self.dir = "/home/equinox/pythobb/pythobb/" # Dir of PythoBB
		self.url = "http://127.0.0.1:8000/"
		self.host = re.search("database = '(.*?)';\n",open(self.dir+"settings.txt","r").read()).group(1)
		self.db = self.connect()

	def connect(self): # Connect to DB
		d = self.modules[1].connect(self.host)
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
		
	def authorize(self, inp):
		import hashlib
		x = Main().execute(q="SELECT * FROM pythobb_users WHERE username='%s'"%(inp[0]),s=False)
		if len([c for c in x]) == 0:
			return ["Invalid username."]
		else:
			uid = [c for c in x][0][-1]
			s = [c for c in x][0][2]
			if hashlib.md5(inp[1]+s).hexdigest() != [c for c in x][0][1]:
				return ["Mismatched password."]
			else:
				return ["Login successful.",uid]

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
				return False
			else:
				if d[0][4] == "":
					avatar = "http://i.imgur.com/JahN5AL.png"
				else:
					avatar = d[0][4]
				return {"username":d[0][0],"registered":d[0][5],"group":d[0][-2],"uid":d[0][-1],"avatar":avatar,"usertitle":d[0][-3]}
		except Exception as e:
			return str("".join(e))

	def create(self,vars):
		import time
		if len(vars) == 6:
			if vars["username"] == "":
				return "Username cannot be null."
			if vars["password"]=="":
				return "Password cannot be null."
			if vars["email"] == "":
				return "Email cannot be null."
			for x in ["username","email"]:
				d = [c for c in Main().execute(q="SELECT * FROM pythobb_users WHERE %s='%s'" % (x,vars[x]))]
				if len(d) != 0:
					return "%s is already in use." % (x)
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
				return len([c for c in Main().execute(q="SELECT * FROM pythobb_users",s=False)])+1
			def sessionID():
				import random,hashlib
				r = random.randrange(2 ** 15,3**14)
				return hashlib.md5(hex(r)+salt()).hexdigest()
			try:
				import hashlib
				s = salt()
				u = str(uid())
				Main().execute(
					q="INSERT INTO pythobb_users VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')" % (
						vars["username"],
						hashlib.md5(vars["password"]+s).hexdigest(),
						s,
						vars["email"],
						vars["avatar"],
						str(time.time()),
						vars["usertitle"],
						vars["group"],
						u
						),
					s = True
					)
				Main().execute(q="INSERT INTO pythobb_sessions VALUES ('%s','%s')" % (sessionID(),u),s=True)
				return True
			except Exception as e:
				return False,str(e)
		else:
			return "Variable \"vars\" (DictType) too short."

class Forums:
	def __init__(self):
		self.types = {"forum":"pythobb_forums","category":"pythobb_cat"}
	
	def get_cat(self):
		cat = [c for c in Main().execute(q="SELECT * FROM {0}".format(self.types["category"]),s=False)]
		return cat
		
	def get_for(self, cid):
		fors = [c for c in Main().execute(q="SELECT * FROM {0} WHERE parent='{1}'".format(self.types["forum"],str(cid)))]
		return fors
		
	def getAmount(self, o, fid):
		if o == "p":
			v = 0
			threads = [t for t in Main().execute(q="SELECT * FROM pythobb_threads WHERE parent='%s'"%(fid),s=False)] # Get threads for counting posts
			for x in threads:
				tid = x[1]
				v += len([c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'"%(tid),s=False)])
			return str(v)
		if o == "t":
			return str(len([t for t in Main().execute(q="SELECT * FROM pythobb_threads WHERE parent='%s'"%(fid),s=False)]))
		
	def genFor(self, array):
		temp = open(Main().dir+"templates/forum.ptmp","r").read()
		s = ""
		for x in array:
			s += str( temp.replace("{[forumname]}",x[0]).replace("{[forumurl]}",Main().url+"forum/{0}/".format(x[1])).replace("{[posts]}","{0} Posts in".format(self.getAmount("p",x[1]))).replace("{[threads]}",self.getAmount("t",x[1])+" Threads")  )
		return s
		
	def genCat(self, array):
		temp = open(Main().dir+"templates/category.ptmp","r").read()
		s = ""
		for x in array:
			cid = x[1]
			s += str( temp.replace("{[catname]}",x[0]).replace("{[forums]}",self.genFor( self.get_for(cid) )) +"<br/>")
		return s
		
	def genThreads(self, array):
		temp = open(Main().dir+"templates/thread.ptmp","r").read()
		s = ""
		for x in array:
			last = [c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'" % (x[2]),s=False)][-1][-1]
			s += str( temp.replace("{[threadname]}",x[0]).replace("{[threadurl]}",Main().url+"forum/{0}/{1}/".format(x[2],x[1])).replace("{[lastpost]}", "Lastpost by "+last.split(":")[0]) )
		return s
		
	def genPosts(self, array, fid, tid):
		temp = open(Main().dir+"templates/posts.ptmp","r").read()
		s = ""
		for x in array:
			s += str( temp.replace("{[fname]}",[t for t in Main().execute(q="SELECT * FROM pythobb_threads WHERE tid='%s'"%(tid),s=False)][0][0] ) )
		return s.replace("{[getCSRF]}","<script>"+open(Main().dir + "templates/js/function.js","r").read()+"doCSRF();</script>").replace("{[csrfToken]}","""<input type="hidden" name="csrfmiddlewaretoken" class="CSRFToken" value="None">""").replace("{[showposts]}",self.generatePosts(fid,tid)).replace("{[fid]}",fid).replace("{[tid]}",tid)
		
	def generatePosts(self, fid, tid):
		temp = open(Main().dir+"templates/post.ptmp","r").read()
		p = 0
		s = ""
		array = [c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'"%(tid),s=False)]
		for x in array:
			p += 1
			usr = x[-1].split(":")[0]
			av = [v for v in Main().execute(q="SELECT * FROM pythobb_users WHERE username='%s'"%(usr),s=False)][0][4]
			s += temp.replace("{[username]}",usr).replace("{[postid]}",x[0]).replace("{[uservatar]}","<img src='%s' class='profava'/>"%(av)).replace("{[content]}",x[2]).replace("{[postnum]}",str(p)).replace("{[permlink]}",Main().url+"forum/{0}/{1}/#{2}".format(fid,tid,x[0]))
		return s
		

class Pages:
	def __init__(self):
		from django.http import HttpResponse
		self.resp = HttpResponse
			
	def getTemplate(self, x, vars=None, t=None, auth=[False,None]):
		import re,json,time
		f = {
			"forumtitle":Main().forum,
			"forumurl":Main().url,
			"csrfToken":"""<input type="hidden" name="csrfmiddlewaretoken" class="CSRFToken" value="None">""",
			"getCSRF":"<script>"+open(Main().dir + "templates/js/function.js","r").read()+"doCSRF();</script>",
			"userblock":self.Userblock(auth[0],auth[1]),
			"respawn":"<script>setTimeout(function(){location.href='%s';},200);</script>" % (Main().url)
			}
		if(vars != None)and(t=="user"):
			u = {
				"avatar":"<img src='%s'/ class='profava'>" % (vars["avatar"]),
				"username":vars["username"],
				"group":vars["group"],
				"uid":vars["uid"],
				"usertitle":vars["usertitle"],
				"registered":time.strftime("%d/%m/%y", time.localtime(float(vars["registered"])))
				}
		elif(vars != None)and(t=="cats"): u = {"category":Forums().genCat(Forums().get_cat())}
		elif(vars != None)and(t=="forum"):
			u = {
				"fname":[c for c in Main().execute(q="SELECT * FROM  pythobb_forums WHERE fid='%s'" % (vars["fid"]),s=False)][0][0],
				"threads":Forums().genThreads(array=[c for c in Main().execute(q="SELECT * FROM pythobb_threads WHERE parent='%s'"%(vars["fid"]),s=False)]),
				"newthread":Main().url+"forum/{0}/newthread/".format(vars["fid"])
				}
		elif(vars != None)and(t=="showthread"):
			u = {
				"newpost":Main().url+"forum/{0}/{1}/#newpost".format(vars["fid"],vars["tid"]),
				"posts":Forums().genPosts(array=[c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'"%vars["tid"],s=False)],fid=vars["fid"],tid=vars["tid"])
				}
		else:
			u = dict()
		y = open(Main().dir + "templates/%s.ptmp" % (x),"r").read()
		for c in re.findall("\{\[(.*?)\]\}",y):
			for q in [f,u]:
				try: y = y.replace("{[%s]}"%(c),q[c])
				except: pass
		return y
		
	def Userblock(self, a1, a2):
		if a1 == True:
			import re
			s = str(open(Main().dir+"templates/userblock_l.ptmp","r").read())
			usr = [v for v in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(a2),s=False)][0][0]
			x = {"forumurl":Main().url,"username":usr}
			for c in re.findall("\{\[(.*?)\]\}",s):
				s = s.replace( "{[%s]}"%(c), x[c] )
			return s
		else:
			return str(open(Main().dir+"templates/userblock_nl.ptmp","r").read().replace("{[forumurl]}",Main().url))

	def Index(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			return self.resp(self.getTemplate("header")+self.getTemplate("index",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
		else:
			return self.resp(self.getTemplate("header")+self.getTemplate("index",vars={},t="cats")+self.getTemplate("footer"))

	def Profile(self, request, username):
		f = User().viewuser(username)
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			if f == False:
				page = self.getTemplate("header")+self.getTemplate("404",auth=[True,uid])+self.getTemplate("footer")
			else:
				page = self.getTemplate("header")+self.getTemplate("profile",vars=f,t="user",auth=[True,uid])+self.getTemplate("footer")
			return self.resp(page)
		else:
			if f == False:
				page = self.getTemplate("header")+self.getTemplate("404")+self.getTemplate("footer")
			else:
				page = self.getTemplate("header")+self.getTemplate("profile",vars=f,t="user")+self.getTemplate("footer")
			return self.resp(page)

	def Login(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			struct = "<script>location.href='%s';</script>"%(Main().url)
		else:
			struct = "%s%s%s" % (self.getTemplate("header"),self.getTemplate("login"),self.getTemplate("footer"))
		return self.resp(struct)
		
	def Register(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			struct = "<script>location.href='%s';</script>"%(Main().url)
		else:
			struct = "%s%s%s" % (self.getTemplate("header"),self.getTemplate("register"),self.getTemplate("footer"))
		return self.resp(struct)
		
	def doLogin(self, request):
		u,p = request.POST["username"],request.POST["password"]
		r = User().authorize(inp=[u,p])
		if r[0] == "Mismatched password.":
			s = "%s%s%s" % (self.getTemplate("header"),self.getTemplate("login").replace("<div class='title login'>Login</div>","<div class='title login' style='background:#EE3535;'>Login</div>"),self.getTemplate("footer"))
		if r[0] == "Invalid username.":
			s = "%s%s%s" % (self.getTemplate("header"),self.getTemplate("login").replace("<div class='title login'>Login</div>","<div class='title login' style='background:#EE3535;'>Login</div>"),self.getTemplate("footer"))
		if r[0] == "Login successful.":
			s = "%s%s%s" % (self.getTemplate("header"),self.getTemplate("successfullogin"),self.getTemplate("footer"))
			#Main().execute(q="UPDATE pythobb_users SET loggedin='1' WHERE uid='%s'" % (r[1]),s=True)
			sid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE uid='%s'" % (r[1]),s=False)][0][0]
		sx = self.resp(s)
		sx.set_cookie('SESSION_ID',sid)
		return sx

	def doRegister(self, request):
		u = request.POST["username"]
		p,p2 = request.POST["password"],request.POST["repassword"]
		e = request.POST["email"]
		if p != p2:
			return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("register").replace("<div class='title login'>Register</div>","<div class='title login' style='background:#EE3535;'>Register - %s</div>" % "Passwords do not match."),self.getTemplate("footer")))
		else:
			s = User().create({"username":u,"password":p,"email":e,"avatar":'',"usertitle":'New User',"group":'default'})
			if s in ["email is already in use.","username is already in use."]:
				return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("register").replace("<div class='title login'>Register</div>","<div class='title login' style='background:#EE3535;'>Register - %s</div>" % s),self.getTemplate("footer")))
			else:
				if s == True:
					return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("registersuccessful"),self.getTemplate("footer")))
				elif s[0] == False:
					return self.resp(s[1])
				else:
					return self.resp(s)

	def doLogout(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			Main().execute(q="UPDATE pythobb_users SET loggedin='0' WHERE uid='%s'" % (uid),s=True)
			sx = self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("logout"),self.getTemplate("footer")))			
			sx.set_cookie('SESSION_ID','')
			return sx
		else:
			return self.resp("<script>location.href='%s';</script>" % (Main().url))

	def doToken(self, request): # If CSRF token is lost
		from django.middleware.csrf import rotate_token
		rotate_token(request)
		o = request.GET["rel"]
		if not o:
			o = Main().url
		return self.resp("<script>location.href='%s';</script>" % (o))
		
	def userCP(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if not uid:
			return self.resp("<script>location.href='%s';</script>"%(Main().url))
		else:
			return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("controlpanel",auth=[True,uid]),self.getTemplate("footer")))

	def modifySettings(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			if(request.POST["avatar"])and(request.POST["avatar"] != ""):
				try:
					r = request.POST["avatar"]
					allowed = [".gif",".png",".jpg"]
					if not "."+str(r)[::-1][0:3][::-1] in allowed:
						return
					else:
						Main().execute(q="UPDATE pythobb_users SET avatar='%s' WHERE uid='%s'" % (r,uid),s=True)
						return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("controlpanel",auth=[True,uid]).replace("<div id='container'>","<div id='container'><div class='msg'>Your settings have been successfully updated.</div>"),self.getTemplate("footer")))
				except Exception as e:
					return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("controlpanel",auth=[True,uid]).replace("<div id='container'>","<div id='container'><div class='msg'>Error, try again. If the problem persists, contain the site admin.</div>"),self.getTemplate("footer")))
			if(request.POST["usertitle"])and(request.POST["usertitle"] != ""):
				try:
					Main().execute(q="UPDATE pythobb_users SET usertitle='%s' WHERE uid='%s'" % (request.POST["usertitle"],uid),s=True)
					return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("controlpanel",auth=[True,uid]).replace("<div id='container'>","<div id='container'><div class='msg'>Your settings have been successfully updated.</div>"),self.getTemplate("footer")))
				except Exception as e:
					return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("controlpanel",auth=[True,uid]).replace("<div id='container'>","<div id='container'><div class='msg'>Error, try again. If the problem persists, contain the site admin.</div>"),self.getTemplate("footer")))
		else:
			return self.resp("<script>location.href='%s';</script>" % (Main().url))
			
	def Forum(self, request, fid):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			return self.resp(self.getTemplate("header")+self.getTemplate("fpage",t="forum",vars={"fid":fid},auth=[True,uid])+self.getTemplate("footer"))
		else:
			return self.resp(self.getTemplate("header")+self.getTemplate("fpage",t="forum",vars={"fid":fid})+self.getTemplate("footer"))

	def Thread(self, request, fid, tid):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			return self.resp(self.getTemplate("header")+self.getTemplate("showthread",auth=[True,uid],vars={"fid":fid,"tid":tid},t="showthread")+self.getTemplate("footer"))
		else:
			return self.resp(self.getTemplate("header")+self.getTemplate("showthread",vars={"fid":fid,"tid":tid},t="showthread")+self.getTemplate("footer"))

	def MakeThread(self, request, fid):
		return self.resp("None")
