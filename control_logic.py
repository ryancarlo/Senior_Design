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
spi_speed = 976000  #spi speed of 488 kHz

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
spi1 = spidev.SpiDev()

spi_setup(spi_shift, 0, 0, spi_speed)
spi_setup(spi0, 1, 0, spi_speed)
spi_setup(spi1, 1, 1, spi_speed)

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

#Sets both of the chip selects to high
spi0.cshigh = True
spi1.cshigh = True

try:
    while(1):
        for k in range(4):
            if (k == 0):
                #First pole of switch is selected (logic_a = 0, logic_b = 0)
                GPIO.output(logic_a, GPIO.LOW)
                GPIO.output(logic_b, GPIO.LOW)
            elif (k == 1):
                #Second pole of switch is selected (logic_a = 0, logic_b = 1)
                GPIO.output(logic_a, GPIO.LOW)
                GPIO.output(logic_b, GPIO.HIGH)
            elif (k == 2):
                #Third pole of switch is selected (logic_a = 1, logic_b = 0)
                GPIO.output(logic_a, GPIO.HIGH)
                GPIO.output(logic_b, GPIO.LOW)
            elif (k == 3):
                #Fourth pole of switch is selected (logic_a = 1, logic_b = 1)
                GPIO.output(logic_a, GPIO.HIGH)
                GPIO.output(logic_b, GPIO.HIGH)
                
            for i in range(16):
                for j in range(4):
                    phase_shifter_val[j] += 0x01

                spi_shift.writebytes(phase_shifter_val)

                GPIO.output(rclk, GPIO.HIGH)
                GPIO.output(rclk, GPIO.LOW)

                #Sets chip select 0 low to enable communication to channel 0
                spi0.cshigh = False

                #Performs SPI transaction for channel 0
                adc0 = spi0.xfer2([primary_reg, secondary_reg0, 0x00])

                #Sets chip select 0 to high and chip select 1 to low to enable communnication to channel 1
                spi0.cshigh = True
                spi1.cshigh = False

                #Performs SPI transaction for channel 1
                adc1 = spi1.xfer2([primary_reg, secondary_reg1, 0x00])

                #Sets chip select 1 to high
                spi1.cshigh = True

                #Extracts the 12-bit values received from SPI transactions for channels 0 and 1
                data0 = ((adc0[1]&0xF) << 8) | adc0[2]
                data1 = ((adc1[1]&0xF) << 8) | adc1[2]
        
                print("channel 0: ", data0, "      channel 1: ", data1)

                time.sleep(0.1)

except KeyboardInterrupt:
    spi_shift.writebytes([0x00, 0x00, 0x00, 0x00])
    GPIO.output(rclk, GPIO.HIGH)
    GPIO.output(rclk, GPIO.LOW)
    GPIO.output(logic_a, GPIO.LOW)
    GPIO.output(logic_b, GPIO.LOW)
    spi_shift.close()
    spi0.close()
    spi1.close()
    GPIO.cleanup()
