import time 
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

motors = MotorKit()

for i in range(36800): # ~ 100 turns 
    motors.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE) #forward / backward flipped due to gear layout
    time.sleep(0.01)
    print('FORWARD: ' + str(i))

for i in range(36800): # ~ 100 turns reverse
    motors.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE) #forward / backward flipped due to gear layout
    time.sleep(0.01)
    print('REVERSE: ' + str(i))


for i in range(36800): # ~ 2 steps forward, 1 step back -- over and over
    motors.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE) #forward / backward flipped due to gear layout
    time.sleep(0.01)
    motors.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE) 
    time.sleep(0.01)
    motors.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE) 
    time.sleep(0.01)
    print('TORTURE: ' + str(i))
    

motors.stepper1.release()