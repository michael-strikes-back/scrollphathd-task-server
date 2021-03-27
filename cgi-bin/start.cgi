#!/usr/bin/env python3

import cgi
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


def print_error(errorMessage):
    if errorMessage is None or errorMessage is '':
        errorMessage = 'There was an error access the task display server, check admin logs in case something went wrong.'

    # $TODO templatize!
    print ('''Content-Type: text/html

<html>
 <head><title>Failed to access task display server.</title></head>
 <body>{0}</body>
</html>
'''.format(errorMessage))


# $TODO belongs in lib
filepath = '/tmp/block.fifo'
def send_start_request():
    with open(filepath, 'w') as file:
        print('star', file=file, end='')
        file.flush()
    return (True, None)


def send_message_request(m):
    maxMessageLen = 0xff

    if (len(m) > maxMessageLen):
        return (False, 'The message is too long. Please limit the line to {0} characters.'.format(maxMessageLen))
        
    lengthInHex = '{:02x}'.format(len(m))

    payload = 'mess'
    payload += lengthInHex
    payload += m

    with open(filepath, 'w') as file:
        print(payload, file=file, end='')
        file.flush()

    return (True, None)


def main():
    cgitb.enable()

    form = cgi.FieldStorage()

    # $TODO everything before output belongs in lib
    runScriptPath = os.path.realpath(os.path.join(sys.path[0], '../www-lib', 'block_run.py'))

    hasMessage = 'message' in form

    success = True
    errorMessage = None

    if not os.path.exists(filepath):
        try:
            Popen([runScriptPath])
        except:
            raise 'Failed to start display service!'

        # $TODO service start-up does not belong in CGI
        # wait for it to start up
        for i in range(10):
            if os.path.exists(filepath):
                success = True
                break
            time.sleep(0.5)

    if not success:
        pass
    elif hasMessage:
        (success, errorMessage) = send_message_request(form['message'].value)
    else:
        (success, errorMessage) = send_start_request()

    if success:
        redirect()
    else:
        print_error(errorMessage)


if __name__ == '__main__':
    main()

