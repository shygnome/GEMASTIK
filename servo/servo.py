from gpiozero import Servo
from time import sleep

myGPIO = 17
myServo = Servo(myGPIO)

while True:
	myServo.mid()
	sleep(1)
	myServo.min()
	sleep(1)
