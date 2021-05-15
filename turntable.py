import board
import display
import os
import requests
import subprocess
import sys
import time
from digitalio import DigitalInOut, Direction
from adafruit_motorkit import MotorKit
from config import Config
from display import Text, Backlight


version = '2021.05.14' 

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


# Settings
ipAddressConfirmed = False
secondsBetweenPhotosConfirmed = False
maxStepsConfirmed = False
statusMessageLifespan = 3.0

ipAddress, secondsBetweenPhotos, maxSteps = Config.read()
protocol = 'http'


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


def configureIP():
	print('DEBUG: Configuring IP...')
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
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
			print('DEBUG: Button L...')
			if modifyingOctet > 1:
				modifyingOctet -= 1
			else:
				modifyingOctet = 4

		# Move to next octet
		elif not buttonR.value:
			print('DEBUG: Button R...')
			if modifyingOctet < 4:
				modifyingOctet += 1
			else:
				modifyingOctet = 1

		# Save update
		if not buttonA.value:
			print('DEBUG: Button A...')
			reconstructIP(octet1, octet2, octet3, octet4)
			Config.write(ipAddress, secondsBetweenPhotos, maxSteps) 
			ipAddressConfirmed = True
		
		time.sleep(0.1)

	if ipAddressConfirmed == True:
		Text.write((promptText, ipAddress), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)

#// ===========================================================================


def configureSecondsBetweenPhotos():
	print('DEBUG: Configure Seconds Between Photos...')
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
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
			Config.write(ipAddress, secondsBetweenPhotos, maxSteps) 
			secondsBetweenPhotosConfirmed = True

		time.sleep(0.1)

	if secondsBetweenPhotosConfirmed == True:
		Text.write((promptText, secondsBetweenPhotos), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)


#// ===========================================================================


def configureMaxSteps():
	print('DEBUG: Configure Max Steps...')
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global maxStepsConfirmed
	global statusMessageLifespan
	
	promptText = 'Max steps: '
	Text.write((promptText, maxSteps), 0, 0)

	while maxStepsConfirmed == False:
		if not buttonU.value:
			if maxSteps < 720:
				maxSteps += 1
			else:
				maxSteps = 0
				Text.write((promptText, maxSteps), 0, 0)
			
		elif not buttonD.value:
			if maxSteps > 0:
				maxSteps -= 1
			else:
				maxSteps = 60
				Text.write((promptText, maxSteps), 0, 0)

		if not buttonA.value:
			Config.write(ipAddress, secondsBetweenPhotos, maxSteps) 
			maxStepsConfirmed = True
		
		time.sleep(0.1)

	if maxStepsConfirmed == True:
		Text.write((promptText, maxSteps), 0, 0, '#00FF00')
		time.sleep(statusMessageLifespan)

#// ===========================================================================


def turn():
	print('DEBUG: Turn...')
	global motors
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global protocol
	global turning

	promptText = 'Starting scan with one frame every ' + str(secondsBetweenPhotos) + ' seconds for up to ' + str(maxSteps) + ' steps...'
	Text.write((promptText,), 0, 0, '#FFFF00')
	print('\n ' + promptText)
	
	for i in range(maxSteps):
		try:
			promptText = 'Scanning...'
			Text.write((promptText, 'Frame: ' + str(i)), 0, 0, '#FFA500')
				
			url = protocol + '://' + ipAddress + '/control/capture/photo'
			response = requests.get(url)
			if response.status_code > 399:
				break
			else:
				time.sleep(secondsBetweenPhotos/2)
				motors.stepper1.onestep()
				time.sleep(secondsBetweenPhotos/2)
		except:
			promptText = 'Could not connect to camera!'
			Text.write((promptText,), 0, 0, '#FF0000')
			time.sleep(statusMessageLifespan)
			configureIP()


	promptText = 'Scan pass complete... '
	Text.write((promptText,), 0, 0, '#0000FF')
	print('\n ' + promptText)
	time.sleep(statusMessageLifespan)
	turning = False


#// ===========================================================================


try:
	echoOff()

	try:
		os.chdir('/home/pi') 
	except:
		pass

	print('\n Turntable ' + version )
	print('\n ----------------------------------------------------------------------')
	time.sleep(2)
	
	configureIP()
	configureSecondsBetweenPhotos()
	configureMaxSteps()

	promptText = 'Press "A" to start a new scan pass... '
	Text.write((promptText,), 0, 0, '#FFFF00')
	
	while True:
		if turning == False:
			if not buttonA.value:
				turning = True
				turn()	
			else:
				promptText = 'Press "A" to start a new scan pass... '
				Text.write((promptText,), 0, 0, '#FFFF00')
		else:
			time.sleep(1)
	
except KeyboardInterrupt:
	Text.clear()
	Backlight.off()
	echoOn()
	sys.exit(1)