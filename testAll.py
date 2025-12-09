import time
import math
import busio
import digitalio
import numpy as np
import pandas as pd
from NIRS import NIRS
from time import sleep
import time
import datetime
import joblib
import requests
import random

# server 169.254.152.179
import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from PIL import Image, ImageDraw, ImageFont

from board import SCK, MOSI, MISO, CE0, D24, D25
import RPi.GPIO as GPIO

from adafruit_rgb_display import color565
import adafruit_rgb_display.ili9341 as ili9341

# Configuration for CS and DC pins:
CS_PIN = CE0
DC_PIN = D25
RESET_PIN = D24
BAUDRATE = 24000000
BUTTON_PIN = 16  # GPIO pin for the button

# Setup GPIO for button
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

# Set the entire image to white
draw.rectangle((0, 0, display.height, display.width), fill=(255, 255, 255))
# Draw axis x, y
draw.line((10, 220, 230, 220), fill=(0, 0, 0))
draw.line((10, 220, 10, 60), fill=(0, 0, 0))

# Draw a triangle
triangle_points = [(230, 218), (230, 222), (234, 220)]
draw.polygon(triangle_points, outline=(0, 0, 0), fill=(0, 0, 0))  # Outline in black, fill in red
triangle_points = [(8, 60), (12, 60), (10, 56)]
draw.polygon(triangle_points, outline=(0, 0, 0), fill=(0, 0, 0))  # Outline in black, fill in red


# image = Image.open("./photos/main.jpg")

# # Scale the image to the smaller screen dimension
# image_ratio = image.width / image.height
# screen_ratio = width / height
# if screen_ratio < image_ratio:
#     scaled_width = image.width * height // image.height
#     scaled_height = height
# else:
#     scaled_width = width
#     scaled_height = image.height * width // image.width
# image = image.resize((scaled_width, scaled_height), Image.BICUBIC)

# # Crop and center the image
# x = scaled_width // 2 - width // 2
# y = scaled_height // 2 - height // 2
# image = image.crop((x, y, x + width, y + height))

# # Display image.
# display.image(image)

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
text = "Mango index Predictor"
draw_text(image, text, (40, 15), 90, fontMono)
# display.image(image)
text1 = "Dry matter"
draw_text(image, text1, (240, 110), 90, font)
# display.image(image)
text2 = "...%"
draw_text(image, text2, (240, 130), 90, fontMono)
# display.image(image)
text3 = "Welcome"
draw_text(image, text3, (100, 110), 90, fontMono)
text4 = "Press X to RUN"
draw_text(image, text4, (60, 130), 90, fontMono)
# text = "900"
# draw_text(image, text, (5, 225), 0, font)
# text = "1700"
# draw_text(image, text, (225, 225), 0, font)
# text = "0"
# draw_text(image, text, (2, 220), 0, font)
display.image(image)

# Main loop to plot a sine wave:
while True:
    # Check if the button is pressed (active low)
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:
        # Print start to display
        text3 = "Welcome"
        draw_text(image, text3, (100, 110), 90, fontMono, fill=(255, 255, 255))
        text4 = "Press X to RUN"
        draw_text(image, text4, (60, 130), 90, fontMono, fill=(255, 255, 255))
        text = "Starting..."
        draw_text(image, text, (60, 130), 90, fontMono, outline=(0,0,0), fill=(255, 128, 128))
        display.image(image)

        # Do NIRS studd
        nirs = NIRS()
        nirs.display_version()

        # Set config. 
        localtime = time.localtime(time.time())
        nirs.sync_device_date_time(localtime.tm_year, localtime.tm_mon, localtime.tm_mday, localtime.tm_wday, localtime.tm_hour, localtime.tm_min, localtime.tm_sec);
        nirs.set_config(8, NIRS.TYPES.COLUMN_TYPE, 220, 10, 900, 1700, 15, 1, "my_cfg8")
        nirs.set_hibernate(False)
        nirs.clear_error_status()
        nirs.set_lamp_on_off(0)
        nirs.set_lamp_on_off(1)
        nirs.set_pga_gain(2)
        # print("Scanning...")
        # Print start to display
        text = "Scanning..."
        draw_text(image, text, (60, 130), 90, fontMono, outline=(0,0,0),  fill=(255, 128, 0))
        display.image(image)

        # Do the scan
        sleep(1)
        nirs.scan(6)
        # Print start to display
        text = "Processing..."
        draw_text(image, text, (60, 130), 90, fontMono, outline=(0,0,0), fill=(0, 128, 255))
        display.image(image)
        sleep(1)
        nirs.set_lamp_on_off(-1)

        results = nirs.get_scan_results()
        # print(results) 
        # df = pd.DataFrame(results)
        # print(df)
        # Get the current date and time
        # current_time = datetime.datetime.now()
        # Format the date and time as 'YYYYMMDDHHMMSS'
        # formatted_time = current_time.strftime('%Y%m%d%H%M%S')
        # Create a CSV filename using the formatted time
        # csv_filename = f'{formatted_time}.csv'

        # df.to_csv("./Data/"+results["scan_time"]+".csv")
        # df.to_csv("./Data/" + csv_filename)
        
        # Function to load the saved PLS model
        def load_pls_model(filename):
            return joblib.load(filename)

        # Reference Intensity values
        reference = [64321,80676,92894,104976,115774,130844,154283,175346,197335,219282,239672,258752,276709,294857,312480,330020,348534,366847,388860,404427,418297,431065,443398,450976,457904,463690,467678,470223,472279,473963,474271,474262,474242,475297,473997,473902,474039,474607,474403,476155,476329,478326,480295,480968,484760,488045,491032,494592,498294,501992,504429,508265,511933,514454,516270,518783,521572,524076,526546,527691,529321,530381,530287,531502,531582,531801,533504,535694,538469,542942,548981,555390,564649,571040,578947,586687,594292,602299,611570,621467,629732,638783,653656,664537,675332,687139,698690,710520,722822,735105,747982,760718,773734,786519,799488,818250,830718,844012,857298,870284,879184,886876,897526,906912,912659,919079,926095,935522,939136,944582,949910,951592,952282,955076,957244,958295,957619,958816,959008,958530,957320,955732,956538,958114,957601,958444,958666,957733,953941,950378,949340,946558,941316,934857,930246,925723,922062,918982,918560,916477,915777,915477,916347,917414,916994,917362,918754,919407,918434,918799,917712,917640,914933,913694,911930,908838,907025,903403,900043,896210,892124,888891,886501,881955,876620,871860,866792,863136,858369,853321,847542,840061,832500,826972,820368,815308,807465,801243,793424,785949,777732,768304,760897,748766,740166,729690,720758,711221,699218,689030,678204,667707,655283,643451,632460,621329,604217,592220,580744,568434,555989,539599,524884,510507,493914,476686,461452,445837,427901,410953,396115,394201,387439,371947,365659,349331,330599,309747,291056,-178936,-178936,2147304711,2147304711,2147304712,2147304712,2147304712,2147304711,-178936]

        # Load the saved model when needed
        loaded_pls_model = load_pls_model('/home/nhatld/Project/test/NIRScanner-Python/pls_model.pkl')

        # Predict y values using the PLS model
        reformat_intensity = []
        reformat_reference = []
        reformat_wavelength = []
        for i, ref_value in enumerate(reference):
            if not math.isnan(ref_value) and ref_value > 0 and ref_value < 1000000:
                if results["intensity"][i] < 0:
                    reformat_intensity.append(0)
                else:
                    reformat_intensity.append(results["intensity"][i])
                reformat_reference.append(reference[i])
                reformat_wavelength.append(results["wavelength"][i])
                
        reflectance = np.array(reformat_intensity) / np.array(reformat_reference)
        absorption = -1 * np.log10(reflectance)

        # Convert reformat_indensity to a NumPy array for easier manipulation
        reformat_indensity_np = np.array(reformat_intensity)
        # reformat_indensity_np = reformat_intensity

        # Standard Normal Variate (SNV)
        mean_intensity = np.mean(reformat_indensity_np, axis=0)
        std_intensity = np.std(reformat_indensity_np, axis=0)
        snv_indensity = (reformat_indensity_np - mean_intensity) / std_intensity

        # Multiplicative Scatter Correction (MSC)
        # Calculate the mean spectrum
        mean_spectrum = np.mean(snv_indensity, axis=0)

        # Perform MSC correction
        msc_indensity = snv_indensity / mean_spectrum

        # print("SNV Indensity:", snv_indensity)
        # print("MSC Indensity:", msc_indensity)

        # Calculate second derivative
        X = savgol_filter(snv_indensity, 30, polyorder = 2,deriv=1)

        y_pred = loaded_pls_model.predict(X.reshape(1,-1))
        y_pred = y_pred[0, 0]
        print("Predicted Dry Material " + "{:.3f}".format(y_pred) + "%")       
        y_pred = map_value(y_pred, 0, 200,  100, 0)
        # Data to be written to the file
        data_to_write = "{:.1f}".format(y_pred)

        # Open the file in write mode ('w' for write, 'a' for append)
        # with open("sample.txt", "w") as file:
        #     file.write(data_to_write)

        # Clear the display
        # display.fill(0)

        # Draw x-axis
        # display.hline(0, display.height // 2, display.width, color565(255, 255, 255))

        # Draw y-axis
        # display.vline(display.width // 2, 0, display.height, color565(255, 255, 255))

        # Delete the hole chart
        draw.rectangle((0, 55, 0+5+230, 55+5+180), fill=(255, 255, 255))

        # Draw axis x, y
        draw.line((10, 220, 230, 220), fill=(0, 0, 0))
        draw.line((10, 220, 10, 60), fill=(0, 0, 0))

        # Draw a triangle
        triangle_points = [(230, 218), (230, 222), (234, 220)]
        draw.polygon(triangle_points, outline=(0, 0, 0), fill=(0, 0, 0))  # Outline in black, fill in red
        triangle_points = [(8, 60), (12, 60), (10, 56)]
        draw.polygon(triangle_points, outline=(0, 0, 0), fill=(0, 0, 0))  # Outline in black, fill in red

        # Set up sine wave parameters
        amplitude = 100
        frequency = 0.05
        # Determine the min and max values dynamically
        min_value = min(results["intensity"])
        max_value = max(results["intensity"])
        print("Max value = " + str(max_value))
        print("Min value = " + str(min_value))
        # Plot line chart from the dictionary
        prev_x, prev_y = None, None
        for x in range(220):
            # Calculate corresponding y value for the sine wave
            # y = int(map_value(math.sin(x * frequency), -1, 1, -amplitude, amplitude) + display.width / 2)
            y = int(map_value(results["intensity"][x], min_value, max_value,  230, 60))
            # Plot the pixel on the display
            # display.pixel(y+20, x+10, color565(0, 0, 0))
            draw.point((x+10, y), fill=(0, 0, 0))
            # Connect points with lines
            if prev_x is not None and prev_y is not None:
                draw.line((prev_x+10, prev_y, x+10, y), fill=(0, 0, 0))
            prev_x, prev_y = x, y

        # Update the display
        text = "900"
        draw_text(image, text, (5, 225), 0, font)
        text = "1700(nm)"
        draw_text(image, text, (225, 225), 0, font)
        text = "0"
        draw_text(image, text, (2, 215), 0, font)
        text = str(max_value) + "(AU)"
        draw_text(image, text, (2, 45), 0, font)

        text2 = str(data_to_write) + "%"
        draw_text(image, text2, (240, 130), 90, fontMono)
        display.image(image)

        # spectrum_data = list(results["intensity"])
        spectrum_data = [random.random() for _ in range(227)]
        mango_indices = {
            'Dry Matter': y_pred,
            'Sugar': random.uniform(10, 15),       # example range
            'Acid': random.uniform(1, 3),          # example range
            'Brix': random.uniform(10, 20)         # example range
        }
        data_to_send = {'spectrum': spectrum_data, 'indices': mango_indices}
        print(data_to_send)
        # requests.post('http://192.168.137.1:5000/data', json=data_to_send)

        # Pause to avoid rapid updates while the button is held down
        time.sleep(0.5)

    # Pause to avoid excessive loop iterations
    time.sleep(0.1)
