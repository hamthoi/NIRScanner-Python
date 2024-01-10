import time
import random
import busio
import digitalio
from board import SCK, MOSI, MISO, CE0, D24, D25

from adafruit_rgb_display import color565
import adafruit_rgb_display.ili9341 as ili9341


# Configuration for CS and DC pins:
CS_PIN = CE0
DC_PIN = D25
RESET_PIN = D24
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)

# Create the ST7789 display:
display = ili9341.ILI9341(
    spi,
    rotation=90,
    width=240,
    height=320,
    baudrate=BAUDRATE,
    cs=digitalio.DigitalInOut(CS_PIN),
    dc=digitalio.DigitalInOut(DC_PIN),
    rst=digitalio.DigitalInOut(RESET_PIN))

# Main loop:
while True:
    # Fill the screen red, green, blue, then black:
    for color in ((255, 0, 0), (0, 255, 0), (0, 0, 255)):
        display.fill(color565(color))
    # Clear the display
    display.fill(0)
    # Draw a red pixel in the center.
    display.pixel(display.width // 2, display.height // 2, color565(255, 0, 0))
    # Pause 2 seconds.
    time.sleep(2)
    # Clear the screen a random color
    display.fill(
        color565(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    )
    # Pause 2 seconds.
    time.sleep(2)