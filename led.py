import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setwarnings(False)

LED1 = 40
LED2 = 38

GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)

GPIO.output(LED1, GPIO.HIGH)
GPIO.output(LED2, GPIO.HIGH)

time.sleep(2)

GPIO.output(LED1, GPIO.LOW)
GPIO.output(LED2, GPIO.LOW)