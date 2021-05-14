import board
import config
import display
import requests
import time
from digitalio import DigitalInOut, Direction
from adafruit_motorkit import MotorKit


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
buttonU = Direction.INPUT

buttonD = DigitalInOut(board.D22)
buttonD = Direction.INPUT


#// ===========================================================================


# Settings
ipAddressConfirmed = False
secondsBetweenPhotosConfirmed = False
maxStepsConfirmed = False
ipAddress, secondsBetweenPhotos, maxSteps = config.Read()
protocol = 'http'


def GetIPOctets():
	try:
		global ipAddress
		splitAddress = ipAddress.split('.')
		return (int(splitAddress[0]), int(splitAddress[1]), int(splitAddress[2]), int(splitAddress[3]))
	except: 
		return (127, 0, 0, 1)


#// ===========================================================================


def ConfigureIP():
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global ipAddressConfirmed
	
	promptText = 'Camera IP address: '
	modifyingOctet = 4

	octet1, octet2, octet3, octet4 = GetIPOctets()
	
	while ipAddressConfirmed == False:
		screenData = []
		screenData.append(promptText)
		screenData.append(ipAddress)
		display.Text.Write(0, 0, screenData)

		# First IP Octet
		if modifyingOctet == 1:
			if not buttonU.value:
				if octet1 < 255:
					octet1 += 1
				else:
					octet1 = 0
				time.sleep(0.5)

			elif not buttonD.value:
				if octet1 > 0:
					octet1 -= 1
				else:
					octet1 = 255
				time.sleep(0.5)

		# Second IP Octet
		elif modifyingOctet == 2:
			if not buttonU.value:
				if (octet2 < 255):
					octet2 += 1
				else:
					octet2 = 0
				time.sleep(0.5)

			elif not buttonD.value:
				if octet2 > 0:
					octet2 -= 1
				else:
					octet2 = 255
				time.sleep(0.5)

		# Third IP Octet
		elif modifyingOctet == 3:
			if not buttonU.value:
				if octet3 < 255:
					octet3 += 1
				else:
					octet3 = 0
				time.sleep(0.5)

			elif not buttonD.value:
				if octet3 > 0:
					octet3 -= 1
				else:
					octet3 = 255
				time.sleep(0.5)

		# Fourth IP Octet
		else:
			if not buttonU.value:
				if octet4 < 255:
					octet4 += 1
				else:
					octet4 = 0
				time.sleep(0.5)

			elif not buttonD.value:
				if octet4 > 0:
					octet4 -= 1
				else:
					octet4 = 255
				time.sleep(0.5)

		# Move to prior Octet
		if not buttonL.value:
			if modifyingOctet > 0:
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
			ipAddress = octet1 + '.' + octet2 + '.' + octet3 + '.' + octet4
			config.Write(ipAddress, secondsBetweenPhotos, maxSteps) 
			ipAddressConfirmed = True

	if ipAddressConfirmed == True:
		screenData = []
		screenData.append(promptText)
		screenData.append(ipAddress)
		display.Text.Write(0, 0, screenData, '#00FF00')
		return True


#// ===========================================================================


def ConfigureSecondsBetweenPhotos():
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global secondsBetweenPhotosConfirmed
	
	promptText = 'Seconds between photos: '
	
	while secondsBetweenPhotosConfirmed == False:
		screenData = []
		screenData.append(promptText)
		screenData.append(str(secondsBetweenPhotos))
		display.Text.Write(0, 0, screenData)
		
		if not buttonU.value:
			if secondsBetweenPhotos < 60:
				secondsBetweenPhotos += 1
			else:
				secondsBetweenPhotos = 0
			time.sleep(0.5)
		elif not buttonD.value:
			if secondsBetweenPhotos > 0:
				secondsBetweenPhotos -= 1
			else:
				secondsBetweenPhotos = 60
			time.sleep(0.5)

		if not buttonA.value:
			config.Write(ipAddress, secondsBetweenPhotos, maxSteps) 
			ipConfirmed = True

	if secondsBetweenPhotosConfirmed == True:
		screenData = []
		screenData.append(promptText)
		screenData.append(str(secondsBetweenPhotos))
		display.Text.Write(0, 0, screenData, '#00FF00')
		return True


#// ===========================================================================


def ConfigureMaxSteps():
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global maxStepsConfirmed
	
	promptText = 'Max steps: '
	
	while maxStepsConfirmed == False:
		screenData = []
		screenData.append(promptText)
		screenData.append(str(maxSteps))
		display.Text.Write(0, 0, screenData)

		if not buttonU.value:
			if maxSteps < 720:
				maxSteps += 1
			else:
				maxSteps = 0
			time.sleep(0.5)
		elif not buttonD.value:
			if maxSteps > 0:
				maxSteps -= 1
			else:
				maxSteps = 60
			time.sleep(0.5)

		if not buttonA.value:
			config.Write(ipAddress, secondsBetweenPhotos, maxSteps) 
			ipConfirmed = True

	if maxStepsConfirmed == True:
		screenData = []
		screenData.append(promptText)
		screenData.append(str(maxSteps))
		display.Text.Write(0, 0, screenData, '#00FF00')
		return True


#// ===========================================================================


def Turn():
	global motors
	global ipAddress
	global secondsBetweenPhotos
	global maxSteps
	global protocol

	promptText = 'Starting scan with one frame every ' + str(secondsBetweenPhotos) + ' seconds for up to ' + str(maxSteps) + ' steps...'
	screenData = []
	screenData.append(promptText)
	display.Text.Write(0, 0, screenData, '#FFFF00')
	
	for i in range(maxSteps):
		url = protocol + '://' + ipAddress + '/control/capture/photo'
		response = requests.get(url)
		if response.status_code > 399:
			break
		else:
			time.sleep(secondsBetweenPhotos/2)
			motors.stepper1.onestep()
			time.sleep(secondsBetweenPhotos/2)

	promptText = 'Scan pass complete... '
	screenData = []
	screenData.append(promptText)
	display.Text.Write(0, 0, screenData, '#0000FF')
	time.sleep(5)
	return True


#// ===========================================================================


try:
	ipConfigured = ConfigureIP
	secondsBetweenPhotosConfigured = ConfigureSecondsBetweenPhotos
	maxStepsConfigured = ConfigureMaxSteps
	while True:
		if turning == False:
			if not buttonA.value:
				Turn()
			else:
				promptText = 'Press "A" to start a new scan pass... '
				screenData.append(promptText)
				display.Text.Write(0, 0, screenData, '#FFFF00')
		else:
			time.sleep(1)
	
except KeyboardInterrupt:
	echoOn()
	sys.exit(1)