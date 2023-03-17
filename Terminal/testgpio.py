import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #11 pin number of rpi
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #13 pin number of rpi

while 1:
    button_4w = GPIO.input(17)
    button_2w = GPIO.input(27)
    if button_4w == False:
        time.sleep(1)
        print("4w pushed")
    if button_2w == False:
        time.sleep(1)
        print("2w pushed!")
