#!/usr/bin/python3

import RPi.GPIO as GPIO
import time

logic_a = 16
logic_b = 18

GPIO.setmode(GPIO.BOARD)

GPIO.setup(logic_a, GPIO.OUT)
GPIO.setup(logic_b, GPIO.OUT)

try:
    while(1):
        GPIO.output(logic_a, GPIO.LOW)
        GPIO.output(logic_b, GPIO.LOW)
        
        time.sleep(1)

        GPIO.output(logic_a, GPIO.LOW)
        GPIO.output(logic_b, GPIO.HIGH)

        time.sleep(1)
        
        GPIO.output(logic_a, GPIO.HIGH)
        GPIO.output(logic_b, GPIO.LOW)

        time.sleep(1)
        
        GPIO.output(logic_a, GPIO.HIGH)
        GPIO.output(logic_b, GPIO.HIGH)

        time.sleep(1)

except KeyboardInterrupt:
    GPIO.output(logic_a, GPIO.LOW)
    GPIO.output(logic_b, GPIO.LOW)
    GPIO.cleanup()
