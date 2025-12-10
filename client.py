import requests
import time
import random
import requests
import time
import random

# Simulate gathering spectral data from a sensor
def gather_data(num_points=227):
    """Return a simulated spectrum as a 1D list of intensities and optional metadata.

    For real hardware, replace this function with the scanner read function that
    returns a 1D array-like of intensity values.
    """
    spectrum_data = [random.random() * 100000 for _ in range(num_points)]
    metadata = {
        'device': 'DLP NIRScan Nano',
        'sample_type': 'unknown',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    return {'spectrum': spectrum_data, 'metadata': metadata}


if __name__ == '__main__':
    # Example server URL (change or comment out when not used)
    # server_url = 'http://127.0.0.1:5000/data'
    server_url = None

    while True:
        data = gather_data()
        print(data)
        # Post data to the server if configured
        if server_url:
            try:
                requests.post(server_url, json=data, timeout=5)
            except Exception as e:
                print('Failed to post data:', e)
        time.sleep(5)  # Send data every 5 seconds
