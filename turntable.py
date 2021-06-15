#!/usr/bin/python3
import board
import display
import os
import requests
import subprocess
import sys
import time
from urllib3.util.retry import Retry
from digitalio import DigitalInOut, Direction
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from config import Config
from display import Text, Backlight


version = '2021.06.14' 

#// ===========================================================================


# Echo/Log Control
outputLog = open('/home/pi/turntable/logs/output.log', 'w+')
errorLog = open('/home/pi/turntable/logs/error.log', 'w+')

os.environ['TERM'] = 'xterm-256color'
def echoOff():
	subprocess.Popen(['stty', '-echo'], shell=True, stdout=subprocess.DEVNULL, stderr=errorLog)
def echoOn():
	subprocess.Popen(['stty', 'echo'], shell=True, stdout=subprocess.DEVNULL, stderr=errorLog)
def clear():
	subprocess.Popen('clear' if os.name == 'posix' else 'cls')
clear()


#// ===========================================================================


# Steppers
motors = MotorKit()
turning = False


#// ===========================================================================


# Inputs
buttonA = DigitalInOut(board.D5)
buttonA.direction = Direction.INPUT

buttonB = DigitalInOut(board.D6)
buttonB.direction = Direction.INPUT

buttonC = DigitalInOut(board.D4)
buttonC.direction = Direction.INPUT

buttonL = DigitalInOut(board.D27)
buttonL.direction = Direction.INPUT

buttonR = DigitalInOut(board.D23)
buttonR.direction = Direction.INPUT

buttonU = DigitalInOut(board.D17)
buttonU.direction = Direction.INPUT

buttonD = DigitalInOut(board.D22)
buttonD.direction = Direction.INPUT


#// ===========================================================================


def getIPOctets():
	try:
		global ipAddress
		splitAddress = ipAddress.split('.')
		return (int(splitAddress[0]), int(splitAddress[1]), int(splitAddress[2]), int(splitAddress[3]))
	except: 
		return (127, 0, 0, 1)


#// ===========================================================================

def reconstructIP(octet1, octet2, octet3, octet4):
	global ipAddress 
	try:
		ipAddress = str(octet1) + '.' + str(octet2) + '.' + str(octet3) + '.' + str(octet4)
	except:
		return ipAddress

#// ===========================================================================

def configureTrigger():
	global trigger
	global triggerConfirmed
	
	promptText = 'Trigger camera: '
	Text.write((promptText, trigger), 0, 0)
		
	while triggerConfirmed == False:
		if not buttonU.value:
			if trigger == 'None':
				trigger += 'Camera.Remote'
			else:
				trigger = 'None'
			Text.write((promptText, trigger), 0, 0)

		elif not buttonD.value:
			if trigger == 'None':
				trigger += 'Camera.Remote'
			else:
				trigger = 'None'
			Text.write((promptText, trigger), 0, 0)

		if not buttonA.value:
			triggerConfirmed = True

		time.sleep(0.1)

	if triggerConfirmed == True:
		Text.write((promptText, trigger), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)

#// ===========================================================================

def configureIP():
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global maxLevels
	global ipAddressConfirmed
	global statusMessageLifespan
	
	modifyingOctet = 4
	octet1, octet2, octet3, octet4 = getIPOctets()

	promptText = 'Camera IP address: '
	Text.write((promptText, ipAddress), 0, 0)

	while ipAddressConfirmed == False:
		# First IP Octet
		if modifyingOctet == 1:
			if not buttonU.value:
				if octet1 < 255:
					octet1 += 1
				else:
					octet1 = 0
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

			elif not buttonD.value:
				if octet1 > 0:
					octet1 -= 1
				else:
					octet1 = 255
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

		# Second IP Octet
		elif modifyingOctet == 2:
			if not buttonU.value:
				if (octet2 < 255):
					octet2 += 1
				else:
					octet2 = 0
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

			elif not buttonD.value:
				if octet2 > 0:
					octet2 -= 1
				else:
					octet2 = 255
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

		# Third IP Octet
		elif modifyingOctet == 3:
			if not buttonU.value:
				if octet3 < 255:
					octet3 += 1
				else:
					octet3 = 0
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

			elif not buttonD.value:
				if octet3 > 0:
					octet3 -= 1
				else:
					octet3 = 255
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

		# Fourth IP Octet
		else:
			if not buttonU.value:
				if octet4 < 255:
					octet4 += 1
				else:
					octet4 = 0
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

			elif not buttonD.value:
				if octet4 > 0:
					octet4 -= 1
				else:
					octet4 = 255
				reconstructIP(octet1, octet2, octet3, octet4)
				Text.write((promptText, ipAddress), 0, 0)

		# Move to prior Octet
		if not buttonL.value:
			if modifyingOctet > 1:
				modifyingOctet -= 1
			else:
				modifyingOctet = 4

		# Move to next octet
		elif not buttonR.value:
			if modifyingOctet < 4:
				modifyingOctet += 1
			else:
				modifyingOctet = 1

		# Save update
		if not buttonA.value:
			reconstructIP(octet1, octet2, octet3, octet4)
			Config.write(ipAddress, secondsBetweenPhotos, maxSteps, maxLevels) 
			ipAddressConfirmed = True
		
		time.sleep(0.1)

	if ipAddressConfirmed == True:
		Text.write((promptText, ipAddress), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)

#// ===========================================================================


def configureSecondsBetweenPhotos():
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global maxLevels
	global secondsBetweenPhotosConfirmed
	global statusMessageLifespan
	
	promptText = 'Seconds between photos: '
	Text.write((promptText, secondsBetweenPhotos), 0, 0)
		
	while secondsBetweenPhotosConfirmed == False:
		if not buttonU.value:
			if secondsBetweenPhotos < 60:
				secondsBetweenPhotos += 1
			else:
				secondsBetweenPhotos = 0
			Text.write((promptText, secondsBetweenPhotos), 0, 0)

		elif not buttonD.value:
			if secondsBetweenPhotos > 0:
				secondsBetweenPhotos -= 1
			else:
				secondsBetweenPhotos = 60
			Text.write((promptText, secondsBetweenPhotos), 0, 0)

		if not buttonA.value:
			Config.write(ipAddress, secondsBetweenPhotos, maxSteps, maxLevels) 
			secondsBetweenPhotosConfirmed = True

		time.sleep(0.1)

	if secondsBetweenPhotosConfirmed == True:
		Text.write((promptText, secondsBetweenPhotos), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)


#// ===========================================================================


def configureMaxSteps():
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global maxLevels
	global maxStepsConfirmed
	global statusMessageLifespan
	
	promptText = 'Max steps: '
	Text.write((promptText, maxSteps), 0, 0)

	while maxStepsConfirmed == False:
		if not buttonU.value:
			if maxSteps < 720:
				maxSteps += 1
			else:
				maxSteps = 10
			Text.write((promptText, maxSteps), 0, 0)
			
		elif not buttonD.value:
			if maxSteps > 10:
				maxSteps -= 1
			else:
				maxSteps = 720
			Text.write((promptText, maxSteps), 0, 0)

		if not buttonA.value:
			Config.write(ipAddress, secondsBetweenPhotos, maxSteps, maxLevels) 
			maxStepsConfirmed = True
		
		time.sleep(0.1)

	if maxStepsConfirmed == True:
		Text.write((promptText, maxSteps), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)


#// ===========================================================================


def configureMaxLevels():
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global maxLevels
	global maxLevelsConfirmed
	global statusMessageLifespan
	
	promptText = 'Max levels: '
	Text.write((promptText, maxLevels), 0, 0)

	while maxLevelsConfirmed == False:
		if not buttonU.value:
			if maxLevels < 720:
				maxLevels += 1
			else:
				maxLevels = 1
			Text.write((promptText, maxLevels), 0, 0)
			
		elif not buttonD.value:
			if maxLevels > 1:
				maxLevels -= 1
			else:
				maxLevels = 720
			Text.write((promptText, maxLevels), 0, 0)

		if not buttonA.value:
			Config.write(ipAddress, secondsBetweenPhotos, maxSteps, maxLevels) 
			maxLevelsConfirmed = True
		
		time.sleep(0.1)

	if maxLevelsConfirmed == True:
		Text.write((promptText, maxLevels), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)


#// ===========================================================================


def capture(url):
	try:
		session = requests.Session()
		retries = Retry(total=20, connect=10, read=10, backoff_factor=0.5)
		session.mount('http://', requests.adapters.HTTPAdapter(max_retries=retries))
		session.get(url) 
		response = session.get(url)
		if response.status_code >= 400:
			promptText = 'Error while capturing image!'
			Text.write((promptText, str(response.status_code), 'Retrying...'), 0, 0, '#FF0000')
			time.sleep(15)
			capture(url)
	except Exception as ex: 
		promptText = 'Could not capture image!'
		Text.write((promptText, str(ex), 'Retrying...'), 0, 0, '#FF0000')
		time.sleep(15)
		capture(url)
		pass
	

#// ===========================================================================


def turn():
	global trigger
	global motors
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global maxLevels
	global protocol
	global turning
	global restarting
	global statusMessageLifespan

	promptText = 'Starting scan of ' + str(maxSteps) + ' frames per ' + str(maxLevels) + ' level(s)...'
	Text.write((promptText,), 0, 0, '#FFFF00')
	print('\n ' + promptText)
	time.sleep(statusMessageLifespan)
	
	for l in range(maxLevels):
		
		for f in range(maxSteps):
			try:
				if not buttonB.value:
					restarting = True
					turning = False
					return

				promptText = 'Scanning...'
				if maxLevels > 1:
					Text.write((promptText, ' ', 'Frame: ' + str(f + 1), ' ', 'Level: ' + str(l + 1)), 0, 0, '#FFA500')
				else:
					Text.write((promptText, ' ', 'Frame: ' + str(f + 1)), 0, 0, '#FFA500')
		
				url = protocol + '://' + ipAddress + '/control/capture/photo'
				try:
					if trigger.strip() != 'None':
						capture(url)
					time.sleep(secondsBetweenPhotos/2)
					try:
						motors.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE) # Set to backward for clockwise rotation of the final gear
					except:
						time.sleep(10)
						pass
					time.sleep(secondsBetweenPhotos/2)
				except Exception as ex:
					promptText = 'Could not connect to camera!'
					Text.write((promptText, str(ex)), 0, 0, '#FF0000')
					time.sleep(statusMessageLifespan)
					print('\n ERROR: ' + str(ex))
					restarting = True
					break
			except Exception as ex:
				promptText = str(ex)
				Text.write((promptText,), 0, 0, '#FF0000')
				time.sleep(statusMessageLifespan)
				print('\n ERROR: ' + str(ex))
				restarting = True
				pass

		if maxLevels > 1:
			if l < maxLevels:
				promptText = 'Moving to next level...'
				Text.write((promptText,), 0, 0, '#FFFF00')
				time.sleep(statusMessageLifespan)
			# Move up 1 layer
			time.sleep(5)
			motors.stepper2.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
			time.sleep(10) # Allows motion to settle to prevent blurry images

	if restarting == False:
		promptText = 'Scan pass complete... '
		Text.write((promptText,), 0, 0, '#0000FF')
		print('\n ' + promptText)
		time.sleep(statusMessageLifespan)
		turning = False


#// ===========================================================================


def restart():
	print('\n Restarting...')
	Text.clear()
	os.execv(sys.argv[0], sys.argv)
	sys.exit(1)


#// ===========================================================================


try:
	echoOff()

	try:
		os.chdir('/home/pi') 
	except:
		pass


	Backlight.on()

	print('\n Turntable ' + version )
	print('\n ----------------------------------------------------------------------')

	# Initialize some variables
	triggerConfirmed = False
	ipAddressConfirmed = False
	secondsBetweenPhotosConfirmed = False
	maxStepsConfirmed = False
	maxLevelsConfirmed = False
	statusMessageLifespan = 3.0
	trigger = 'Camera.Remote'
	ipAddress, secondsBetweenPhotos, maxSteps, maxLevels = Config.read()
	protocol = 'http'
	restarting = False

	# Configure scan
	configureTrigger()
	if trigger.strip() != 'None':
		configureIP()
	else: 
		ipAddressConfirmed = True
	configureSecondsBetweenPhotos()
	configureMaxSteps()
	configureMaxLevels()

	# Get ready..
	while restarting == False:
		if turning == False:
			if not buttonA.value:
				# Go! Go! Go!
				turning = True
				turn()	
			else:
				promptText = 'Press and hold the gray button to start a new scan'
				Text.write((promptText,), 0, 0, '#FFFF00')
				time.sleep(2)
		else:
			time.sleep(1)

	restart()
	
except KeyboardInterrupt:
	Text.clear()
	Backlight.off()
	echoOn()
	sys.exit(1)

	