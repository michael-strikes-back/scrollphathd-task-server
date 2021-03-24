#!/usr/bin/env python3

import cgitb
import os
from subprocess import Popen
import time

def main():

	cgitb.enable()

	redirectURL = '/'

	# $TODO belongs in lib
	filepath = '/tmp/block.fifo'

	try:
		# $TODO next ~4 lines belong in lib
		if os.path.exists(filepath):
			with open(filepath, 'w') as file:
				print('stop', file=file, end='')
				file.flush()
	except:
		raise 'Failed to stop display service!'

	print ('''Status: 303 See other
Location: {0}

'''.format(redirectURL))

#<html>
# <head>
#   <meta http-equiv="refresh" content="0;url={0}" />
#   <title>You are going to be redirected</title>
# </head>
# <body>
#  Redirecting... <a href="{0}">Click here if you are not redirected.</a>
# </body>
#</html>
#'''.format(redirectURL))

if __name__ == '__main__':
	main()

