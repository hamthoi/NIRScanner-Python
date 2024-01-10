# NIRScanner Nano Python wrapper.
# Created by Jintao Yang on 2020/11/23
#!/usr/bin/python3.8


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from NIRS import NIRS
from time import sleep
import time
import datetime
import joblib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import math


def main():
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
    print("Scanning...")
    sleep(1)
    nirs.scan(6)
    sleep(1)
    nirs.set_lamp_on_off(-1)
    results = nirs.get_scan_results()
    print(results)
    df = pd.DataFrame(results)
    #print(df)
    # Get the current date and time
    current_time = datetime.datetime.now()
    # Format the date and time as 'YYYYMMDDHHMMSS'
    formatted_time = current_time.strftime('%Y%m%d%H%M%S')
    # Create a CSV filename using the formatted time
    csv_filename = f'{formatted_time}.csv'

    # df.to_csv("./Data/"+results["scan_time"]+".csv")
    df.to_csv("./Data/" + csv_filename)
    
    # Function to load the saved PLS model
    def load_pls_model(filename):
        return joblib.load(filename)

    # Reference Intensity values
    reference = [64321,80676,92894,104976,115774,130844,154283,175346,197335,219282,239672,258752,276709,294857,312480,330020,348534,366847,388860,404427,418297,431065,443398,450976,457904,463690,467678,470223,472279,473963,474271,474262,474242,475297,473997,473902,474039,474607,474403,476155,476329,478326,480295,480968,484760,488045,491032,494592,498294,501992,504429,508265,511933,514454,516270,518783,521572,524076,526546,527691,529321,530381,530287,531502,531582,531801,533504,535694,538469,542942,548981,555390,564649,571040,578947,586687,594292,602299,611570,621467,629732,638783,653656,664537,675332,687139,698690,710520,722822,735105,747982,760718,773734,786519,799488,818250,830718,844012,857298,870284,879184,886876,897526,906912,912659,919079,926095,935522,939136,944582,949910,951592,952282,955076,957244,958295,957619,958816,959008,958530,957320,955732,956538,958114,957601,958444,958666,957733,953941,950378,949340,946558,941316,934857,930246,925723,922062,918982,918560,916477,915777,915477,916347,917414,916994,917362,918754,919407,918434,918799,917712,917640,914933,913694,911930,908838,907025,903403,900043,896210,892124,888891,886501,881955,876620,871860,866792,863136,858369,853321,847542,840061,832500,826972,820368,815308,807465,801243,793424,785949,777732,768304,760897,748766,740166,729690,720758,711221,699218,689030,678204,667707,655283,643451,632460,621329,604217,592220,580744,568434,555989,539599,524884,510507,493914,476686,461452,445837,427901,410953,396115,394201,387439,371947,365659,349331,330599,309747,291056,-178936,-178936,2147304711,2147304711,2147304712,2147304712,2147304712,2147304711,-178936]

    # Load the saved model when needed
    loaded_pls_model = load_pls_model('pls_model.pkl')

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
    
    # Data to be written to the file
    data_to_write = "{:.3f}".format(y_pred)

    # Open the file in write mode ('w' for write, 'a' for append)
    with open("sample.txt", "w") as file:
        file.write(data_to_write)

    # plt.plot(reformat_wavelength, reformat_intensity, '-r',  label='intensity')     
    # plt.plot(reformat_wavelength, reflectance, '-g',  label='reflectance')
    # plt.plot(reformat_wavelength, absorption,  '-b', label='absorption')
           
    # plt.xlabel("wavelength")
    # plt.ylabel("intensity-ratio")
    # plt.title("NIR Scan Spectrum")
    # plt.legend(loc='upper right', fontsize=7) # label position
    # plt.show()

if __name__ == "__main__":
    main()
