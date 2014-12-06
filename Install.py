import sqlite3,os

queries = [
	"CREATE TABLE pythobb_users (username text,password text,salt text,email text,avatar text,regt text,groups text,uid text,loggedin text)",
	"CREATE TABLE pythobb_sessions (sessionid text, uid text)"
	]

def getFiles():
	try:
		os.system("git clone https://github.com/iEquinox-/PythoBB-vA-0.2B-.git")
		os.system("apt-get install python-pip")
		os.system("pip install Django==1.7.1")
		return True
	except Exception as e:
		return "Error. Are you logged into root? (%s)" % str(e)
	
def doQueries():
	global queries
	s = sqlite3.connect(raw_input("Host: "))
	try:
		for q in queries:
			s.cursor().execute(q)
		s.commit()
		return True
	except Exception as e:
		return str(e)
	
if __name__ == "__main__":
	print "If you haven't aleady installed Django, pip, and PythoBB, please login to root before running this script."
	s = raw_input("Have you installed Django, pip, and PythoBB? [y/n]")
	if s == "n":
		print getFiles()
		print doQueries()
	else:
		print doQueries()
