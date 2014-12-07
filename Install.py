class PageOut():
	def __init__(self):
		
		dir = "/home/equinox/pythobb/pythobb/"
		self.url = "http://127.0.0.1:8000/"
				
		from django.http import HttpResponse
		self.dir = dir
		self.resp = HttpResponse
		self.globals = [
			"""<head>
			<title>PythoBB Install Script</title>
			<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>
			<link href='http://fonts.googleapis.com/css?family=Raleway:100' rel='stylesheet' type='text/css'>
			<link href='https://raw.githubusercontent.com/iEquinox-/PythoBB-vA-0.2B-/master/templates/css/global.css' rel='stylesheet' type='text/css'>
			<script>%s</script>
			</head>
			<div id='header'>
			<a href='http://127.0.0.1:8000/'>PythoBB</a>
			</div>""" % (open(dir+"templates/js/function.js","r").read()+"doCSRF();"),
			"<br/><br/><div id='footer'>&copy; 2014-2015 PythoBB</div>"
			]
		self.page = """<div id='userblock'></div><div id='container'>
			<div id='cont' class='profile'>
			<img src='http://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/2000px-Python-logo-notext.svg.png' class='profava'/>
			<div id='inf'>Python</div>
			<div id='inf' style='margin-top:-80px'>Django</div>
			<br/><div class='hr'></div><br/>
			
			<form action='/admin/doConfigure/' method='post'>
				<input type='hidden' value='' name='csrfmiddlewaretoken' class='CSRFToken'/>
				<input type='text' class='fieldtext' name='dir' placeholder='Directory'><br/>
				<input type='text' class='fieldtext' name='db' placeholder='Database'><br/>
				<input type='text' class='fieldtext' name='aduser' placeholder='Username'><br/>
				<input type='password' class='fieldtext' name='pass' placeholder='Password'><br/>
				<input type='password' class='fieldtext' name='repass' placeholder='Retype Password'><br/>
				<input type='text' class='fieldtext' name='email' placeholder='Email'><br/>
				<input type='submit' value='Configure' class='fieldtext'/>
			</form>
			
			</div>
			</div><div id='bottomblock'></div>"""
		
	def Init(self,request):
		return self.resp(self.globals[0]+self.page+self.globals[1])
		
	def Configure(self, c=None, v=None):
		if(c and v):
			import sqlite3,hashlib
			queries = [
				"CREATE TABLE pythobb_users (username text,password text,salt text,email text,avatar text,regt text,usertitle text,groups text,uid text)",
				"CREATE TABLE pythobb_sessions (sessionid text, uid text)",
				"CREATE TABLE pythobb_cat (category text,cid text,permissions text)",
				"CREATE TABLE pythobb_forums (forum text,fid text,parent text,permissions text)",
				"CREATE TABLE pythobb_threads (thread text,tid text,parent text)",
				"CREATE TABLE pythobb_posts (pid text, parent text,content text,inf text)"
				]
			s = sqlite3.connect(c["database"])
			for query in queries:
				s.cursor().execute(query)
			s.cursor().execute("INSERT INTO pythobb_users VALUES ('{0}','{1}','{2}','{3}','','{4}','Administrator','admin','1')".format(v["username"],v["password"],v["salt"],v["email"],v["time"]))
			s.cursor().execute("INSERT INTO pythobb_sessions VALUES ('{0}','1')".format(hashlib.md5(c["new"]+c["renew"]).hexdigest()))
			f = open(c["directory"]+"settings.txt","w")
			
			settings = ""
			for v in ["directory","database"]:
				settings += "%s = '%s';\n" % (v,c[v])
			
			f.write(settings)
			f.close()
			s.commit()

	def doConfigure(self,request):
		if request.POST["pass"] != request.POST["repass"]:
			return self.resp(self.globals[0]+self.page.replace("<div id='userblock'></div>","<div id='userblock' style='background:#EE3535;color:#FFF;'><ul><li>Passwords do not match.</li></ul></div>")+self.globals[1])
		else:
			import hashlib,random,string,time
			def salt(): return str("".join([random.choice( list( string.ascii_letters + "+_)(*&^%$#@!" ) ) for x in range(0,5)]))
			cdata     = {"directory":request.POST["dir"],"database":request.POST["dir"]+request.POST["db"],"new":salt(),"renew":salt()}
			salty = salt()
			variables = {"username":request.POST["aduser"],"password":hashlib.md5(request.POST["pass"]+salty).hexdigest(),"salt":salty,"email":request.POST["email"],"time":time.time()}
			self.Configure(c=cdata,v=variables)			
			f = open(self.dir+"/install","w")
			f.write("True")
			f.close()
			return self.resp("<script>location.href='%s';</script>" % self.url)
