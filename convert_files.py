from cr2fits import cr2fits
import os

def convert_all(path):
    for (p, d, files) in os.walk(path):
        for filename in files:
            if filename.endswith('.CR2'): 
                # TODO: Add progress bar
                print("Converting \'" + filename + "\' to .FITS")

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
