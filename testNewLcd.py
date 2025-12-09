import time
import math
import busio
import digitalio
from board import SCK, MOSI, MISO, CE0, D24, D25

from adafruit_rgb_display import color565
import adafruit_rgb_display.ili9341 as ili9341

from PIL import Image, ImageDraw, ImageFont

# Configuration for CS and DC pins:
CS_PIN = CE0
DC_PIN = D25
RESET_PIN = D24
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)

# Create the ILI9341 display:
display = ili9341.ILI9341(
    spi,
    rotation=90,
    width=240,
    height=320,
    baudrate=BAUDRATE,
    cs=digitalio.DigitalInOut(CS_PIN),
    dc=digitalio.DigitalInOut(DC_PIN),
    rst=digitalio.DigitalInOut(RESET_PIN)
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if display.rotation % 180 == 90:
    height = display.width  # we swap height/width to rotate it to landscape!
    width = display.height
else:
    width = display.width  # we swap height/width to rotate it to landscape!
    height = display.height
image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)
image = Image.open("./photos/main.jpg")

# Scale the image to the smaller screen dimension
image_ratio = image.width / image.height
screen_ratio = width / height
if screen_ratio < image_ratio:
    scaled_width = image.width * height // image.height
    scaled_height = height
else:
    scaled_width = width
    scaled_height = image.height * width // image.width
image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

# Crop and center the image
x = scaled_width // 2 - width // 2
y = scaled_height // 2 - height // 2
image = image.crop((x, y, x + width, y + height))

# Display image.
display.image(image)

# Function to map a value from one range to another
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
fontMono = ImageFont.truetype('/home/nhatld/Downloads/VCR_OSD_MONO_1.001.ttf', 18)

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Define a function to create text thing
def draw_text(image, text, position, angle, font, outline=(256, 256, 256), fill=(0, 0, 0)):
    draw = ImageDraw.Draw(image)
    (text_width, text_height) = draw.textsize(text, font=font)
    
    # Calculate the coordinates for the rectangle
    x1, y1 = position
    x2, y2 = x1 + text_width, y1 + text_height
    
    # Draw the rectangle
    draw.rectangle([position, (x2, y2)], outline=outline, fill=(255, 255, 255))
    
    # Draw the text
    draw.text(position, text, font=font, fill=fill)

# Draw template
text = "NIR Firmness Predictor"
draw_text(image, text, (40, 15), 90, fontMono)
display.image(image)
text1 = "Scan time"
draw_text(image, text1, (240, 100), 90, font, outline=(0,0,0))
display.image(image)
text2 = "DM=?%"
draw_text(image, text2, (240, 130), 90, fontMono, outline=(0,0,0))
display.image(image)

# Main loop to plot a sine wave:
while True:
    # Clear the display
    # display.fill(0)

    # Draw x-axis
    # display.hline(0, display.height // 2, display.width, color565(255, 255, 255))

    # Draw y-axis
    # display.vline(display.width // 2, 0, display.height, color565(255, 255, 255))

    # Set up sine wave parameters
    # amplitude = 100
    # frequency = 0.05

    # Plot the sine wave
    # for y in range(display.height):
    #     # Calculate corresponding y value for the sine wave
    #     x = int(map_value(math.sin(y * frequency), -1, 1, -amplitude, amplitude) + display.width / 2)

    #     # Plot the pixel on the display
    #     display.pixel(x, y, color565(0, 0, 0))

    # Update the display
    # display.display()
    text = "DM=100%"
    draw_text(image, text, (240, 130), 90, fontMono)
    display.image(image)

    # Pause for a moment
    time.sleep(5)
