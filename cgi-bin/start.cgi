#!/usr/bin/env python3

import cgitb
import os
from subprocess import Popen
import sys
import time

def main():

	cgitb.enable()

	redirectURL = '/'

	# $TODO everything before output belongs in lib
	filepath = '/tmp/block.fifo'
	runScriptPath = os.path.realpath(os.path.join(sys.path[0], '../www-lib', 'block_run.py'))

	if not os.path.exists(filepath):
		try:
			Popen([runScriptPath])
		except:
			raise 'Failed to start display service!'

	# wait for it to start up
	tries = 10
	while (tries > 0) and (not os.path.exists(filepath)):
		time.sleep(0.5)
		tries -= 1
	
	if os.path.exists(filepath):
		with open(filepath, 'w') as file:
			print('star', file=file, end='')
			file.flush()

	print ('''Status: 303 See other
Location: {0}

'''.format(redirectURL))

#	print ('''Content-Type: text/html
#Location: {0}
#
#<html>
# <head>
#   <meta http-equiv="refresh" content="0;url={0}" />
#   <title>You are going to be redirected</title>
# </head>
# <body>
#  Redirecting... <a href="{0}">Click here if you are not redirected.</a><br>
# </body>
#</html>
#'''.format(redirectURL))

if __name__ == '__main__':
	main()

