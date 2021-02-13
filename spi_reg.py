#!/usr/bin/python3

import spidev
import RPi.GPIO as GPIO
import time

rclk = 7

GPIO.setmode(GPIO.BOARD)

GPIO.setup(rclk, GPIO.OUT)

GPIO.output(rclk, GPIO.LOW)

spi = spidev.SpiDev()

spi.open(1,0)

spi.max_speed_hz = 976000

to_send = [0x00, 0x00, 0x00, 0x00]

try:
    while(1):
        for i in range(16):
            for j in range(4):
                to_send[j] = to_send[j] + 0x1

            spi.writebytes(to_send)

            GPIO.output(rclk, GPIO.HIGH)

            GPIO.output(rclk, GPIO.LOW)

            time.sleep(0.1)

except KeyboardInterrupt:
    spi.writebytes([0x00, 0x00, 0x00, 0x00])
    GPIO.output(rclk, GPIO.HIGH)
    GPIO.output(rclk, GPIO.LOW)
    spi.close()
    GPIO.cleanup()
