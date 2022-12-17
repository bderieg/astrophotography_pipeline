import os

def combine_darks(path):
    red_dark = []
    green_dark = []
    blue_dark = []
    for (p, d, files) in os.walk(path):
        for filename in files:
            if filename.startswith('dark') and filename.endswith('.fits'):
                if 'G' in filename:
                    if len(green_dark) < 1:
                        # green_dark = 
