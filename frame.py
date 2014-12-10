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
			
	def Check(self, uid):
		group = [c for c in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(uid),s=False)][0][-2]
		if group == "banned":
			return 0
		else:
			return 1

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
			threads = [t for t in Main().execute(q="SELECT * FROM pythobb_threads WHERE parent='%s'"%(fid),s=False)]
			for x in threads:
				tid = x[1]
				v += len([c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'"%(tid),s=False)])
			return str(v)
		if o == "t":
			s = 0
			t = [t for t in Main().execute(q="SELECT * FROM pythobb_threads WHERE parent='%s'"%(fid),s=False)]
			for p in t:
				x = [c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'" % p[1],s=False)]
				if len(x) == 0:
					s += 1
			return str(int(len(t) - s))
		
	def genFor(self, array):
		temp = open(Main().dir+"templates/forum.ptmp","r").read()
		s = ""
		for x in array:
			s += str( temp.replace("{[forumname]}",x[0]).replace("{[forumurl]}",Main().url+"forum/{0}/".format(x[1])).replace("{[posts]}","{0} Posts in".format(self.getAmount("p",x[1]))).replace("{[threads]}",self.getAmount("t",x[1])+" Threads")  )
		return s
		
	def genCat(self, array):
		temp = open(Main().dir+"templates/category.ptmp","r").read()
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
			if len([p for p in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'"%(x[1]),s=False)]) > 0:
				last = [c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'" % (x[1]),s=False)][-1][-1]
				s += str( temp.replace("{[threadname]}",x[0]).replace("{[threadurl]}",Main().url+"forum/{0}/{1}/".format(x[2],x[1])).replace("{[lastpost]}", "Last post by "+last.split(":")[0]) )
				last = ""
		return s
		
	def genPosts(self, _uid_, array, fid, tid, loggedin):
		if loggedin == False: makepost = open(Main().dir+"templates/nopost.ptmp","r").read()
		if loggedin == True: makepost = str(open(Main().dir+"templates/makepost.ptmp","r").read()).replace("{[csrfToken]}","""<input type="hidden" name="csrfmiddlewaretoken" class="CSRFToken" value="None">""").replace("{[fid]}",fid).replace("{[tid]}",tid)
		temp = open(Main().dir+"templates/posts.ptmp","r").read()
		s = str( temp.replace("{[fname]}",[t for t in Main().execute(q="SELECT * FROM pythobb_threads WHERE tid='%s'"%(tid),s=False)][0][0] ) )
		return s.replace("{[getCSRF]}","<script>"+open(Main().dir + "templates/js/function.js","r").read()+"doCSRF();</script>").replace("{[csrfToken]}","""<input type="hidden" name="csrfmiddlewaretoken" class="CSRFToken" value="None">""").replace("{[showposts]}",self.generatePosts(_uid_,fid,tid)).replace("{[fid]}",fid).replace("{[tid]}",tid).replace("{[makepost]}",makepost)
		
	def generatePosts(self, uid, fid, tid):
		temp = open(Main().dir+"templates/post.ptmp","r").read()
		p = 0
		s = ""
		array = [c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'"%(tid),s=False)]
		for x in array:
			p += 1
			usr = x[-1].split(":")[0]
			if uid != None:
				if str(uid) == str([c for c in Main().execute(q="SELECT * FROM pythobb_users WHERE username='%s'"%(usr),s=False)][0][-1]):
					delButton = """<a href='%sforum/%s/%s/deletePost/{[postid]}/' class='minibutton delete' style='float:right;margin-top:-5px;'>Delete</a>""" % (Main().url,fid,tid)
				else:
					if [q for q in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(uid),s=False)][0][-2] == "admin":
						delButton = """<a href='%sforum/%s/%s/deletePost/{[postid]}/' class='minibutton delete' style='float:right;margin-top:-5px;'>Delete</a>""" % (Main().url,fid,tid)
					else:
						delButton = ""
			else:
				delButton = ""
			av = [v for v in Main().execute(q="SELECT * FROM pythobb_users WHERE username='%s'"%(usr),s=False)][0][4]
			s += temp.replace("{[deletepost]}",delButton).replace("{[username]}",usr).replace("{[postid]}",x[0]).replace("{[uservatar]}","<img src='%s' class='profava'/>"%(av)).replace("{[content]}", BBCode().Parse(x[2]) ).replace("{[postnum]}",str(p)).replace("{[permlink]}",Main().url+"forum/{0}/{1}/#{2}".format(fid,tid,x[0]))
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
				"posts":Forums().genPosts(_uid_=auth[1],array=[c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'"%vars["tid"],s=False)],fid=vars["fid"],tid=vars["tid"],loggedin=auth[0])
				}
		elif(vars != None)and(t=="administrator"):
			u = {
				"categories":Admin().generateCategories(),
				"members":Admin().generateMembers()
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
			if "admin" in [c for c in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(a2),s=False)][0][7].split(","):
				acp = "<li><a href='%s'>Admin CP</a></li>" % (Main().url+"admin/")
			else:
				acp = ""
			if [x for x in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(a2),s=False)][0][-2] == "banned":
				x = {"forumurl":"","username":usr,"admincp":"","logout":"","usercp":""}
			else:	
				x = {"forumurl":Main().url,"username":usr,"admincp":acp,"logout":"<li style='float:right;'><a href='{[forumurl]}member/logout/'>Logout</a></li>","usercp":"<li><a href='/member/controlpanel/'>User CP</a></li>"}
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
			if User().Check(uid) == 1:
				return self.resp(self.getTemplate("header")+self.getTemplate("index",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
			else:
				return self.resp(self.getTemplate("header")+self.getTemplate("banned",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
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
			if User().Check(uid) == 0:
				return self.resp(self.getTemplate("header")+self.getTemplate("banned",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
			else:
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
			sx = self.resp(s)
		if r[0] == "Invalid username.":
			s = "%s%s%s" % (self.getTemplate("header"),self.getTemplate("login").replace("<div class='title login'>Login</div>","<div class='title login' style='background:#EE3535;'>Login</div>"),self.getTemplate("footer"))
			sx = self.resp(s)
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
			if User().Check(uid) == 0:
				return self.resp(self.getTemplate("header")+self.getTemplate("banned",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
			else:
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
			import re
			if(request.POST["avatar"])and(request.POST["avatar"] != ""):
				try:
					r = request.POST["avatar"]
					rava = re.findall("(.*?)\.(png|PNG|gif|GIF|jpg|JPG)",r)
					if len(rava) == 0:
						return
					else:
						if len(rava) >= 1:
							rava = rava[0]
						Main().execute(q="UPDATE pythobb_users SET avatar='%s' WHERE uid='%s'" % (r,uid),s=True)
						return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("controlpanel",auth=[True,uid]).replace("<div id='container'>","<div id='container'><div class='msg'>Your settings have been successfully updated.</div>"),self.getTemplate("footer")))
				except Exception as e:
					return self.resp("%s%s%s" % (self.getTemplate("header"),self.getTemplate("controlpanel",auth=[True,uid]).replace("<div id='container'>","<div id='container'><div class='msg'>Error, try again. If the problem persists, contact the site admin.</div>"),self.getTemplate("footer")))
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
			if User().Check(uid) == 0:
				return self.resp(self.getTemplate("header")+self.getTemplate("banned",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
			else:
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
			if User().Check(uid) == 0:
				return self.resp(self.getTemplate("header")+self.getTemplate("banned",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
			else:
				if len([c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'" % (tid),s=False)]) == 0:
					return self.resp(self.getTemplate("header")+self.getTemplate("showthread",auth=[True,uid]).replace("<a href='{[newpost]}' class='postbit_button'>New Post</a>","").replace("<br/><br/><br/>","").replace("{[posts]}","<div style='text-align:center;color:#FFF;background:#222;padding:10px;border-radius:3px;font-family:tohama,droid sans,sans-serif;'>Invalid thread.</div>")+self.getTemplate("footer"))
				else:
					return self.resp(self.getTemplate("header")+self.getTemplate("showthread",auth=[True,uid],vars={"fid":fid,"tid":tid},t="showthread")+self.getTemplate("footer"))
		else:
			if len([c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE parent='%s'" % (tid),s=False)]) == 0:
				return self.resp(self.getTemplate("header")+self.getTemplate("showthread").replace("<a href='{[newpost]}' class='postbit_button'>New Post</a>","").replace("<br/><br/><br/>","").replace("{[posts]}","<div style='text-align:center;color:#FFF;background:#222;padding:10px;border-radius:3px;font-family:tohama,droid sans,sans-serif;'>Invalid thread.</div>")+self.getTemplate("footer"))
			else:
				return self.resp(self.getTemplate("header")+self.getTemplate("showthread",vars={"fid":fid,"tid":tid},t="showthread")+self.getTemplate("footer"))

	def MakeThread(self, request, fid):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if not uid:
			return self.resp("<script>location.href='%s';</script>"%(Main().url+"member/login/"))
		else:
			if User().Check(uid) == 0:
				return self.resp(self.getTemplate("header")+self.getTemplate("banned",vars={},t="cats",auth=[True,uid])+self.getTemplate("footer"))
			else:
				return self.resp(self.getTemplate("header")+self.getTemplate("makethread",auth=[True,uid]).replace("{[fid]}",fid)+self.getTemplate("footer"))
		
	def MakePost(self, request, fid, tid):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if not uid:
			return self.resp("<script>location.href='%s';</script>" % (Main().url))
		else:
			def genPid():
				return str(len([c for c in Main().execute(q="SELECT * FROM pythobb_posts",s=False)]) + 1)
			import time
			content = request.POST["postContent"]
			username = [c for c in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(uid),s=False)][0][0]
			Main().execute(q="INSERT INTO pythobb_posts VALUES ('%s','%s','%s','%s')" % (genPid(),tid,content,(username+":"+str(time.time()))),s=True)
			return self.resp("<script>location.href='%s';</script>" % (Main().url+"forum/%s/%s/"%(fid,tid)))
			
	def DeletePost(self, request, fid, tid, pid):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if not uid:
			return self.resp("<script>location.href='%s';</script>" % (Main().url))
		else:
			x = [c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE pid='%s'" % (pid),s=False)]
			username = x[0][-1].split(":")[0]
			uuid = [c for c in Main().execute(q="SELECT * FROM pythobb_users WHERE username='%s'" % (username),s=False)]
			if uid == uuid[0][-1]:
				Main().execute(q="UPDATE pythobb_posts SET parent='' WHERE pid='%s'"%(pid),s=True)
				return self.resp("<script>location.href='%sforum/%s/%s/';</script>" % (Main().url,fid,tid ))
			else:
				if [p for p in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(uid),s=False)][0][-2] != "admin":
					return self.resp("<script>location.href='%sforum/%s/%s/#%s';</script>" % (Main().url,fid,tid,pid ))
				else:
					Main().execute(q="UPDATE pythobb_posts SET parent='' WHERE pid='%s'"%(pid),s=True)
					return self.resp("<script>location.href='%sforum/%s/%s/';</script>" % (Main().url,fid,tid ))

	def ProcessNThread(self, request, fid):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			import time
			def genTid():
				return str(len([c for c in Main().execute(q="SELECT * FROM pythobb_threads",s=False)]) + 1)
			def genPid():
				return str(len([c for c in Main().execute(q="SELECT * FROM pythobb_posts",s=False)]) + 1)
			tid = genTid()
			Main().execute("INSERT INTO pythobb_threads VALUES ('%s','%s','%s')" % (request.POST["threadname"],tid,fid),s=True)
			Main().execute("INSERT INTO pythobb_posts VALUES ('%s','%s','%s','%s')" % (genPid(),tid,request.POST["threadcontent"],"%s:%s"%(str([p for p in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(uid),s=False)][0][0]),str(time.time()))),s=True)
			return self.resp("<script>location.href='%s';</script>" % (Main().url+"forum/{0}/{1}/".format(fid,tid)))
		else:
			return self.resp("<script>location.href='%s';</script>" % (Main().url+"member/login/"))
			
	def Administrator(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			groups = [x for x in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(uid),s=False)][0][7].split(",")
			if not "admin" in groups:
				return self.resp("<script>location.href='%s';</script>" % (Main().url))
			else:
				return self.resp(
					self.getTemplate("header") + 
					self.getTemplate("admin",auth=[True,uid],t="administrator",vars={}).replace("{[emsg]}","") +
					self.getTemplate("footer")
					)
		else:
			return self.resp("<script>location.href='%s';</script>" % (Main().url))

class Admin:
	def __init__(self):
		from django.http import HttpResponse
		self.resp = HttpResponse
		
	def Add(self, request):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			if request.POST["add_catname"] != "":
				r = request.POST["add_catname"].split("}")
				if len(r) > 2:
					return self.resp(
						Pages().getTemplate("header") + 
						Pages().getTemplate("admin",auth=[True,uid],t="administrator",vars={}).replace("{[emsg]}","<div class='error'>Too many parents to forum \"%s\".</div>" % (r[-1])) +
						Pages().getTemplate("footer")
						)
				else:
					if len(r) == 1:
						def genCid():
							return str(int(len([x for x in Main().execute(q="SELECT * FROM pythobb_cat",s=False)]) + 1))
						Main().execute(q="INSERT INTO pythobb_cat VALUES ('%s','%s','x')" % (r[0],genCid()),s=True)
						msg = "<div class='success'>Category succesfully added.</div>"
					if len(r) == 2:
						def genFid():
							return str(int(len([x for x in Main().execute(q="SELECT * FROM pythobb_forums",s=False)]) + 1))
						Main().execute(q="INSERT INTO pythobb_forums VALUES ('%s','%s','%s','x')" % (r[1],genFid(),r[0]),s=True)
						msg = "<div class='success'>Forum succesfully added.</div>"
					return self.resp(
						Pages().getTemplate("header") + 
						Pages().getTemplate("admin",auth=[True,uid],t="administrator",vars={}).replace("{[emsg]}",msg) +
						Pages().getTemplate("footer")
						)
			else:
				return self.resp(
					Pages().getTemplate("header") + 
					Pages().getTemplate("admin",auth=[True,uid],t="administrator",vars={}).replace("{[emsg]}","<div class='error'>Invalid request sent.</div>") +
					Pages().getTemplate("footer")
					)
		else:
			return self.resp("<script>location.href='%s';</script>"%(Main().url))
			
			
	def Configure(self, request, cid=None, fid=None):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			if cid:
				Main().execute(q="DELETE FROM pythobb_cat WHERE cid='%s'"%(cid),s=True)
				Main().execute(q="DELETE FROM pythobb_forums WHERE parent='%s'"%(cid),s=True)
				return self.resp("<script>location.href='%sadmin/';</script>" % (Main().url))
			if fid:
				Main().execute(q="DELETE FROM pythobb_forums WHERE fid='%s'"%(fid),s=True)
				return self.resp("<script>location.href='%sadmin/';</script>" % (Main().url))
		else:
			return self.resp("<script>location.href='%s';</script>"%(Main().url))
			
	def ToggleBan(self, request, userid):
		if request.COOKIES.has_key("SESSION_ID"):
			sessionID = request.COOKIES["SESSION_ID"]
			if(len(sessionID)>0):
				uid = [x for x in Main().execute(q="SELECT * FROM pythobb_sessions WHERE sessionid='%s'" % (sessionID),s=False)][0][-1]
			else:
				uid = None
		else:
			uid = None
		if uid:
			groups = [c for c in Main().execute(q="SELECT * FROM pythobb_users WHERE uid='%s'"%(userid),s=False)][0][6]
			if not "banned" in groups.split(","):
				Main().execute(q="UPDATE pythobb_users SET groups='banned' WHERE uid='%s'"%(userid),s=True)
				return self.resp("<script>location.href='%sadmin/';</script>"%(Main().url))
			else:
				Main().execute(q="UPDATE pythobb_users SET groups='default' WHERE uid='%s'"%(userid),s=True)
				return self.resp("<script>location.href='%sadmin/';</script>"%(Main().url))
		else:
			return self.resp("<script>location.href='%s';</script>"%(Main().url))
		
	def generateCategories(self):
		s = ""
		for x in [c for c in Main().execute(q="SELECT * FROM pythobb_cat",s=False)]:
			s += "<div class='catf'><a href='javascript:;' class='"+x[1]+"'>%s</a><br/>%s</div>" % ( (x[0] + " ("+x[1]+") <a href='%sadmin/delete/category/%s/' class='modif'/>Remove</a><br/>" % (Main().url,x[1])), self.generateForums(x[1]) )
		return s
		
	def generateForums(self, cid):
		s = ""
		for x in [c for c in Main().execute(q="SELECT * FROM pythobb_forums WHERE parent='%s'"%(cid),s=False)]:
			s += "<div class='forum'> - " + x[0] + " <a href='%sadmin/delete/forum/%s/' class='modif'/>Remove</a></div><br/>" % (Main().url,x[1])
		return s
		
	def generateMembers(self):
		s = ""
		for x in [c for c in Main().execute(q="SELECT * FROM pythobb_users",s=False)]:
			if x[-1] != "1":
				if x[-2] == "banned":
					s += "<div class='catf'><a href='/user/"+x[0]+"/'>%s</a></div>" % ( (x[0] + " ("+x[-1]+") <a href='%sadmin/ban/user/%s/' class='modif'/>Unban</a><br/>" % (Main().url,x[-1])) )
				else:
					s += "<div class='catf'><a href='/user/"+x[0]+"/'>%s</a></div>" % ( (x[0] + " ("+x[-1]+") <a href='%sadmin/ban/user/%s/' class='modif'/>Ban</a><br/>" % (Main().url,x[-1])) )
			else:
				s += "<div class='catf'><a href='/user/"+x[0]+"/'>%s</a></div>" % ( (x[0] + " ("+x[-1]+") <br/>" ) )
		return s

class BBCode():
	# BBCode Parser
	def __init__(self):
		import re
		self.modules = [re]
		
	def Parse(self, content):
		q = self.modules[0].findall("\[(quote)=\"(\d+)\"\]",content,self.modules[0].IGNORECASE)
		if len(q) == 0:
			return content
		else:
			pid = q[0][1]
			post = [c for c in Main().execute(q="SELECT * FROM pythobb_posts WHERE pid='%s'"%(pid),s=False)]
			if len(post) == 0:
				return content.replace("[%s=\"%s\"]" % (q[0][0],q[0][1]), "")
			else:
				user = post[0][-1].split(":")[0]
				text = post[0][-2]
				return content.replace("[%s=\"%s\"]" % (q[0][0],q[0][1]), self.Parse("<div class='quoteblock'><div class='cite'>%s wrote:</div><div class='quote'>%s</div></div>" % (user, text)))
