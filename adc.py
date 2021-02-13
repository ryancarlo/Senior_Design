#!/usr/bin/python3

#import spidev library
import spidev
import time

#Create spi objects
spi0 = spidev.SpiDev()
spi1 = spidev.SpiDev()

def spi_setup(spiObject, port, device, max_speed):
    #Enables SPI ports for Raspberry Pi to SPI device communication
    spiObject.open(port, device)
    #Sets the max speed for spi communication
    spiObject.max_speed_hz = max_speed

spi_setup(spi0, 1, 0, 488000)
spi_setup(spi1, 1, 1, 488000)

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

#Sets both of the chip selects to high
spi0.cshigh = True
spi1.cshigh = True

try:
    while(1):
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

        time.sleep(0.5)

except KeyboardInterrupt:
    spi0.close()
    spi1.close()
