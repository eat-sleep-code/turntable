import time 
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from 

motors = MotorKit()

for i in range(36800):
    motors.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    print(str(i))
    time.sleep(0.01)