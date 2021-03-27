#!/usr/bin/env python3

import cgitb
import os
from subprocess import Popen
import sys
import time

def redirect():
    print ('''Status: 303 See other
Location: /

''')

#   print ('''Content-Type: text/html
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


def print_error():
    # $TODO templatize!
    print ('''Content-Type: text/html

<html>
 <head><title>Failed to access task display server.</title></head>
 <body>There was an error access the task display server, check admin logs in case something went wrong.</body>
</html>
''')


# $TODO belongs in lib
filepath = '/tmp/block.fifo'
def send_start_request():
    with open(filepath, 'w') as file:
        print('star', file=file, end='')
        file.flush()


def main():
    cgitb.enable()

    # $TODO everything before output belongs in lib
    runScriptPath = os.path.realpath(os.path.join(sys.path[0], '../www-lib', 'block_run.py'))

    success = False
    if not os.path.exists(filepath):
        try:
            Popen([runScriptPath])
        except:
            raise 'Failed to start display service!'

        # $TODO service start-up does not belong in CGI
        # wait for it to start up
        for i in range(10):
            if os.path.exists(filepath):
                send_start_request()
                success = True
                break
            time.sleep(0.5)
    else:
        send_start_request()
        success = True

    if success:
        redirect()
    else:
        print_error()


if __name__ == '__main__':
    main()

