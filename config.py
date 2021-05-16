import json
import subprocess

configFile = '/home/pi/turntable/turntable.json'

class Config:

	def read():
		global configFile
		ipAddress = subprocess.getoutput('hostname -I').split(' ')[0] #Only if turntable board is also running camera, but serves as a "safe" default value
		secondsBetweenPhotos = 5
		maxSteps = 200
		maxLevels = 1
		try:	
			with open(configFile) as turntableConfiguration:
				configList = json.load(turntableConfiguration)
				for configItem in configList: # data[] ?
					ipAddress = configItem['ipAddress']
					secondsBetweenPhotos = configItem['secondsBetweenPhotos']
					maxSteps = configItem['maxSteps']
					maxLevels = configItem['maxLevels']
		except:
			print('\n Configuration file not found')
			pass
		return(ipAddress, secondsBetweenPhotos, maxSteps, maxLevels)


	def write(ipAddress, secondsBetweenPhotos = 5, maxSteps = 200, maxLevels = 1): 
		global configFile
		try:
			configList = {}
			configList.append({
				'ipAddress': str(ipAddress),
				'secondsBetweenPhotos': int(secondsBetweenPhotos),
				'maxSteps': int(maxSteps),
				'maxLevels': int(maxLevels)
			})

			with open(configFile, 'w') as turntableConfiguration:
				json.dump(configList, turntableConfiguration, indent=4)
		
			return True
		except Exception as ex:
			print(str(ex))
			return False
