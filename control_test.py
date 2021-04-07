#!/usr/bin/python3

#import libraries
import spidev
import RPi.GPIO as GPIO
import time

#Function to setup up spi parameters for created spi objects
def spi_setup(spiObject, port, device, max_speed):
    #Enables SPI ports for Raspberry Pi to SPI device communication
    spiObject.open(port, device)
    #Sets the max speed for spi communication
    spiObject.max_speed_hz = max_speed

#variables
rclk = 15           #pin for rclk for the shift registers
logic_a = 16        #pin for the logic a input of the switches
logic_b = 18        #pin for the logic b input of the switches
spi_speed = 488000  #spi speed of 488 kHz

#Setup Raspberry Pi GPIO
GPIO.setmode(GPIO.BOARD)

#Set rclk to an output
GPIO.setup(rclk, GPIO.OUT)
GPIO.setup(logic_a, GPIO.OUT)
GPIO.setup(logic_b, GPIO.OUT)

#Initialize rclk to be low
GPIO.output(rclk, GPIO.LOW)

#Create spi objects
spi_shift = spidev.SpiDev()
spi0 = spidev.SpiDev()

spi_setup(spi_shift, 1, 0, spi_speed)
spi_setup(spi0, 0, 0, spi_speed)

#Sets up the first 8 bits that will be sent to the ADC
#Five leading zeros     Start Bit    SGL/DIFF Bit    D2
#     00000                 1             1          0
primary_reg = 0x07 & 0x06   

#Sets up the second set of 8 bits that will be sent to the ADC
#   D1   D0                     Don't Care Bits
#(2 bits to determine the           XXXXXX
#channel of the ADC)
secondary_reg0 = 0 << 6
secondary_reg1 = 1 << 6

#Phase shifter values [PS1, PS2, PS3, PS4]
phase_shifter_val = [0x00, 0x00, 0x00, 0x00]

counter = 0x00

try:
    while(1):
    
        GPIO.output(logic_a, 0x02 & counter)
        GPIO.output(logic_b, 0x01 & counter)

        for i in range(63):

            phase_shifter_val = [(val + 0x01) if val< 63 else 0 for val in phase_shifter_val]

            spi_shift.writebytes(phase_shifter_val)

            GPIO.output(rclk, GPIO.HIGH)
            GPIO.output(rclk, GPIO.LOW)

            #Performs SPI transaction for channel 0
            adc0 = spi0.xfer2([primary_reg, secondary_reg0, 0x00])

            #Performs SPI transaction for channel 1
            adc1 = spi0.xfer2([primary_reg, secondary_reg1, 0x00])

            #Extracts the 12-bit values received from SPI transactions for channels 0 and 1
            data0 = ((adc0[1]&0xF) << 8) | adc0[2]
            data1 = ((adc1[1]&0xF) << 8) | adc1[2]
        
            print("channel 0: ", data0, "      channel 1: ", data1)

            time.sleep(.1)

        counter += 1

except KeyboardInterrupt:
    spi_shift.writebytes([0x00, 0x00, 0x00, 0x00])
    GPIO.output(rclk, GPIO.HIGH)
    GPIO.output(rclk, GPIO.LOW)
    GPIO.output(logic_a, GPIO.LOW)
    GPIO.output(logic_b, GPIO.LOW)
    spi_shift.close()
    spi0.close()
    #spi1.close()
    GPIO.cleanup()
