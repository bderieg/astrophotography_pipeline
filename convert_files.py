from cr2fits import cr2fits
import os
from tqdm.auto import tqdm

def convert_all(path):
    for (p, d, files) in os.walk(path):
        # Initialize progress bar
        progress_bar = tqdm(range(len(files)+1), desc="Converting all files to .fits", leave=False)
        for filename in files:
            if filename.endswith('.CR2'): 
                for color in range(3):
                    # Read in CR2 image
                    inpfile = cr2fits.cr2fits(path + "/" + filename, color)
                    inpfile.read_cr2()
                    ## Convert to numpy array
                    full_img = inpfile.read_pbm(inpfile.pbm_bytes)
                    # Get individual color array
                    im_color = inpfile.get_color(full_img, inpfile.colorInput)
                    # Output to fits
                    fits_color = inpfile.create_fits(im_color)
                    dest = inpfile._generate_destination(inpfile.filename, inpfile.colorInput)
                    inpfile.write_fits(fits_color, dest)
            progress_bar.update(1)
