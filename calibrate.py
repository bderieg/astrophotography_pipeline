import os
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np

def combine_darks(path):
    red_dark = np.empty(0)
    green_dark = np.empty(0)
    blue_dark = np.empty(0)
    for (p, d, files) in os.walk(path):
        for filename in files:
            if filename.startswith('dark') and filename.endswith('.fits'):
                data = np.asarray(fits.open(path + "/" + filename)[0].data)
                if 'R' in filename:
                    if red_dark.size < 1:
                        red_dark = data
                    else:
                        red_dark = (red_dark + data)/2
                elif 'G' in filename:
                    if green_dark.size < 1:
                        green_dark = data
                    else:
                        green_dark = (green_dark + data)/2
                elif 'B' in filename:
                    if blue_dark.size < 1:
                        blue_dark = data
                    else:
                        blue_dark = (blue_dark + data)/2
    fits.writeto(path + '/' + 'full_dark_R.fits', red_dark)
    fits.writeto(path + '/' + 'full_dark_G.fits', green_dark)
    fits.writeto(path + '/' + 'full_dark_B.fits', blue_dark)
