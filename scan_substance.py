#!/usr/bin/env python3
"""Simple example: perform one scan and return a 1D NumPy array of intensities.

Usage:
    python3 scan_substance.py [--save-csv]

If the native `_NIRScanner` extension or attached device isn't available the script
falls back to a simulated spectrum for testing.
"""
import argparse
import time
import os
from datetime import datetime

import numpy as np

try:
    from NIRS import NIRS
    HAS_NIRS = True
except Exception as e:
    # If the wrapper or native lib is unavailable, fall back to simulation
    print("Warning: real NIRS wrapper not available, falling back to simulated data.")
    HAS_NIRS = False


def acquire_spectrum(n_repeats=1, save_csv=False):
    """Return (wavelengths, intensities) as NumPy arrays.

    - wavelengths: 1D array of wavelength (nm) or None if not provided
    - intensities: 1D array of intensity (AU)
    """
    if HAS_NIRS:
        nirs = NIRS()
        # Example config: adjust for your needs
        try:
            nirs.set_config(8, NIRS.TYPES.HADAMARD_TYPE, 228, n_repeats, 900, 1700, 7)
        except Exception:
            # If set_config signature or values differ, ignore and continue
            pass
        # Turn lamp on
        try:
            nirs.set_lamp_on_off(1)
        except Exception:
            pass
        # Wait a bit for lamp to stabilize
        time.sleep(1.0)
        # Perform scan
        nirs.scan(n_repeats)
        results = nirs.get_scan_results()
        # Turn lamp off
        try:
            nirs.set_lamp_on_off(-1)
        except Exception:
            pass

        wavelengths = results.get('wavelength', None)
        intensities = results.get('intensity', None)
        if intensities is None:
            raise RuntimeError('Device returned no intensity data')
        wavelengths = np.array(wavelengths) if wavelengths is not None else None
        intensities = np.array(intensities)
    else:
        # Simulate wavelengths and intensities
        wavelengths = np.linspace(900, 1700, 227)
        intensities = np.abs(np.sin(np.linspace(0, 6.28, 227)) * 5e4 + np.linspace(1e4, 8e4, 227))

    # Optionally save CSV
    if save_csv:
        os.makedirs('Data', exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = os.path.join('Data', f'{timestamp}.csv')
        if wavelengths is None:
            # save only intensities
            np.savetxt(filename, intensities, delimiter=',', header='intensity', comments='')
        else:
            arr = np.vstack([wavelengths, intensities]).T
            np.savetxt(filename, arr, delimiter=',', header='wavelength_nm,intensity', comments='')
        print(f'Saved scan to {filename}')

    return wavelengths, intensities


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save-csv', action='store_true', help='Save a CSV of the scan into Data/')
    parser.add_argument('--repeats', type=int, default=1, help='Number of repeats to perform')
    args = parser.parse_args()

    wl, ints = acquire_spectrum(n_repeats=args.repeats, save_csv=args.save_csv)
    print('Scan result: intensities shape =', ints.shape)
    # For convenience print first 10 values
    print('First 10 intensity values:', ints[:10].tolist())

    # Return a 1D array (intensities) for downstream pipelines
    return ints


if __name__ == '__main__':
    main()
