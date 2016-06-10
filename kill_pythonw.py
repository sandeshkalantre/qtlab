#script to kill process pythonw.exe

import os

def proc_kill(proc_name):
	try:
		killed = os.system('taskkill /F /im ' +  proc_name)
	except Exception, e:
		killed = 0
	return killed
proc_kill("pythonw.exe")
