import os
dir = os.path.dirname(
	os.path.dirname(
		__file__
		)
	)

cde = __name__ + __file__

def getInstall():
	try:
		f = open(dir + "install.lock","r").read()
		if not cde in f:
			return 0
		else:
			return 1
	except Exception as e:
		return 0

class Django:
	def __init__(self):
		import os
		self.modules = [os]
		self.djver = "1.7.1" # Built for 1.7.1
		self.Install()

	def Install(self):
		self.modules[0].system(
			"sudo apt-get install python-pip" #Assumes APT-GET method
			)
		self.modules[0].system(
			"pip install Django==" + self.djver
			)

class Install():
	def __init__(self):
		print "<PythoBB> This program will prompt you multiple times to see if the current circumstances are compatible with PythoBB. Only \"y\" or \"n\" are accepted answers."
		r = raw_input("Is this being ran with root? ")
		i = raw_input("Are both Pip AND Django correctly installed? ")
		if(r == y):
			if(i == y):
				self.Continue()
			else:
				Django()
		else:
			if(i == y):
				self.Continue()
			else:
				print "Please run this program as root to install Django."

	def Continue(self):
		print "Ok"

if __name__ == "__main__":
	is_install = getInstall()
	if is_install == 0:
		Install()
