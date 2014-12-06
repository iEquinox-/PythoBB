import sqlite3,os,json

sl = dict()
dir = None

queries = [
	"CREATE TABLE pythobb_users (username text,password text,salt text,email text,avatar text,regt text,groups text,uid text,loggedin text)",
	"CREATE TABLE pythobb_sessions (sessionid text, uid text)"
	]

def getFiles():
	global s
	try:
		os.system("git clone https://github.com/iEquinox-/PythoBB-vA-0.2B-.git")
		sl["pythobb"] = json.dumps(True)
		os.system("apt-get install python-pip")
		sl["pip"] = json.dumps(True)
		os.system("pip install Django==1.7.1")
		sl["django"] = json.dumps(True)
		return True
	except Exception as e:
		return "Error. Are you logged into root? (%s)" % str(e)
	
def doQueries():
	global queries,s,dir
	h = dir+raw_input("DB Name: ")
	s = sqlite3.connect(h)
	try:
		for q in queries:
			s.cursor().execute(q)
		s.commit()
		sl["host"] = json.dumps(h)
		return True
	except Exception as e:
		return str(e)
		
def writeSettings():
	global sl,dir
	f = open(dir+"settings.txt","w")
	c = ""
	format = "%s = '%s';\n"
	for x in sl:
		c += format%(x,json.loads(sl[x]))
	f.write(c)
	f.close()
	
def insertAdmin():
	global sl
	import hashlib,random,string,time
	def salt():
		c = ""
		for x in range(0,5):
			c += random.choice(list(string.ascii_letters+"+_)(*&^%$#@!"))
		return c
	print "Inserting admin account... You can only do this once, so be sure you don't have any typos."
	u = raw_input("Username: ")
	p = raw_input("Password: ")
	e = raw_input("Email: ")
	sa = salt()
	p = hashlib.md5(p+sa).hexdigest()
	s = sqlite3.connect(json.loads(sl["host"]))
	s.cursor().execute("INSERT INTO pythobb_users VALUES ('{0}','{1}','{2}','{3}','','{4}','admin','1','0')".format(u,p,sa,e,int(time.time())))
	re = salt()
	s.cursor().execute("INSERT INTO pythobb_sessions VALUES ('{0}','1')".format(hashlib.md5(re+salt()).hexdigest()))
	s.commit()
	
if __name__ == "__main__":
	dir = raw_input("Directory: ")
	print "If you haven't aleady installed Django, pip, and PythoBB, please login to root before running this script."
	s = raw_input("Have you installed Django, pip, and PythoBB? [y/n]")
	if s == "n":
		print getFiles()
		print doQueries()
		writeSettings()
		insertAdmin()
	else:
		sl["pythobb"] = json.dumps(True)
		sl["pip"] = json.dumps(True)
		sl["django"] = json.dumps(True)
		print doQueries()
		writeSettings()
		insertAdmin()
