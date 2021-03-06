#!/usr/bin/env python3

import datetime
import math
import os
import scrollphathd as sphd
import sys 
import threading
import time
import traceback

done = False
start = True
startMessage = ''

blockDelta = datetime.timedelta(minutes = 25)
# either show a message every 5 minutes, or half of the block
messageDelta = min(datetime.timedelta(minutes = 5), blockDelta / 2)

###
# displayThreadRun
# entry point of display thread. handles reading global state and updating timer display on the scrollbot.
#
def displayThreadRun():

    global done, start, startMessage

    # note, this doesn't account for delays in sphd
    frames_per_second= 30

    nextTime = None
    previousTextToDisplay = ''
    textToDisplay = ''
    messageWidth = 0
    messageStartTime = None

    frame_delay_seconds= 1.0/frames_per_second

    try:

        sphd.set_brightness(0.33)
        sphd.rotate(180)

        while not done:

            currTime = datetime.datetime.now()

            if start:
                nextTime = currTime + blockDelta
                start = False
                messageWidth = 0
                if startMessage != None and startMessage != '':
                    messageStartTime = currTime
                else:
                    messageStartTime = None

            if currTime > nextTime:
                start = True
            elif messageWidth > 0:
                messageWidth -= 1
                sphd.scroll()
            elif messageStartTime != None and currTime >= messageStartTime:
                # prep the countdown
                messageWidth = sphd.display.calculate_string_width(startMessage)
                # schedule next start time
                messageStartTime = currTime + messageDelta
                # text, plus some blank time
                textToDisplay = startMessage + '    '
            else:
                deltaSeconds = (nextTime - currTime).total_seconds()
                deltaMinutes = math.ceil(deltaSeconds / 60)
                if deltaMinutes == 1:
                    textToDisplay = '::{0}'.format(math.ceil(deltaSeconds))
                else:
                    textToDisplay = ':{0}'.format(deltaMinutes)

            if textToDisplay != previousTextToDisplay:
                sphd.clear()
                sphd.write_string(textToDisplay, fill_background=True)

            sphd.show()
            time.sleep(frame_delay_seconds)
            previousTextToDisplay = textToDisplay

        sphd.clear()
    except Exception as e:
        # check i2c group membership for executing user?
        traceback.print_exc(file=sys.stderr)
        done = True 

def log(s, l):
    print('[{0}] {1}'.format(datetime.datetime.now(), s), file=l)

###
# main
# entry point of program execution
#
# arguments:
#    argv: unused, left in case arguments are useful later on
def main(argv):
    global done, start, startMessage

    with open('/var/log/www-data/block_run.log', 'a') as fileLog:

        fifoPath = '/tmp/block.fifo'
        log('Starting up', fileLog)

        try:
            os.mkfifo(fifoPath)
        except OSError as e:
            log('Failed to create FIFO at {0}: {1}'.format(fifoPath, e), fileLog)
            fileLog.flush()
            # probably another instance of this program is running and beat us to it
            sys.exit()

        try:
            displayThread = threading.Thread(target=displayThreadRun)

            displayThread.start()

            log('opening pipe for read', fileLog)

            try:
                while not done:
                    with open(fifoPath, 'r') as file:
                        log('awaiting command', fileLog)
                        command = file.read(4)
                        if command == 'stop':
                            log('stopping per command', fileLog)
                            done = True
                        elif command == 'star':
                            log('restarting per command', fileLog)
                            startMessage = ''
                            start = True
                        elif command == 'mess':
                            log('restarting per command', fileLog)
                            messageSizeHex = file.read(2)
                            try:
                                messageSize = int(messageSizeHex, 16)
                            except ValueError:
                                log('got invalid hex for message size: {0}'.format(messageSizeHex))
                            else:
                                startMessage = file.read(messageSize).strip()
                                log('... with message "{0}"'.format(startMessage), fileLog)
                                start = True
                    time.sleep(0.5)
                                        
            except Exception as e:
                log('stopping due to exception: {0}'.format(e), fileLog)
                done = True

            log('cleaning up', fileLog)

            displayThread.join()

        finally:
            os.remove(fifoPath)

        log('done', fileLog)

        ## Check if this is needed still
        #except:
        #	exc_text= traceback.format_exc()
        #	with open("/home/pi/scroll_message_error.log", "w") as f:
        #		f.write("Exception! {}\n".format(exc_text))
        #		f.write("Terminating.\n")
        #		f.write("\n")

if __name__ == "__main__":
    main(sys.argv[1:])

