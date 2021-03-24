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

blockDelta = datetime.timedelta(minutes = 25)

###
# displayThreadRun
# entry point of display thread. handles reading global state and updating timer display on the scrollbot.
#
def displayThreadRun():

	global done, start

	# note, this doesn't account for delays in sphd
	frames_per_second= 30
	space_delay_seconds= 0.5

	nextTime = None
	previousTextToDisplay = ''
	textToDisplay = ''

	frame_delay_seconds= 1.0/frames_per_second
	spaces= ' ' * int(space_delay_seconds * frames_per_second)

	try:

		sphd.set_brightness(0.33)
		sphd.rotate(180)

		while not done:
			if start:
				nextTime = datetime.datetime.now() + blockDelta
				start = False
			currTime = datetime.datetime.now()
			if currTime > nextTime:
				start = True
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
	global done, start

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
				with open(fifoPath, 'r') as file:
					while not done:
						log('awaiting command', fileLog)
						command = file.read(4)
						if command == 'stop':
							log('stopping per command', fileLog)
							done = True
						elif command == 'star':
							log('restarting per command', fileLog)
							start = True
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

