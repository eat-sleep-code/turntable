import json
import subprocess

configFile = 'turntable.json'

class Config:
	
	def read(self):
		global configFile
		ipAddress = subprocess.getoutput('hostname -I').split(' ')[0] #Only if turntable board is also running camera, but serves as a "safe" default value
		secondsBetweenPhotos = 5
		maxSteps = 200
		try:	
			with open(configFile) as turntableConfiguration:
				configList = json.load(turntableConfiguration)
				for configItem in configList: # data[] ?
					ipAddress = configItem['ipAddress']
					secondsBetweenPhotos = configItem['secondsBetweenPhotos']
					maxSteps = configItem['maxSteps']
		except:
			print('No configuration found...')
			pass
		return(ipAddress, secondsBetweenPhotos, maxSteps)


	def write(self, ipAddress, secondsBetweenPhotos = 5, maxSteps = 200): 
		global configFile
		try:
			configList = {}
			configList.append({
				'ipAddress': str(ipAddress),
				'secondsBetweenPhotos': int(secondsBetweenPhotos),
				'maxSteps': int(maxSteps)
			})

			with open(configFile, 'w') as turntableConfiguration:
				json.dump(configList, turntableConfiguration, indent=4)
		
			return True
		except:
			return False
