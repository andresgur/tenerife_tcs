from astropy.io import fits
import numpy as np
import argparse

ap = argparse.ArgumentParser(description='Print information from the images headers')
ap.add_argument("input_images", nargs="+", help="Input images to be inspected", type=str)
args = ap.parse_args()

images = args.input_images

for image in images:
    hdul = fits.open(image)
    primary_header = hdul[0].header
    #print(primary_header)
    print("\n ---------- \n Image", image)
    print("Exposure time:", primary_header["EXPTIME"])
    print("Target:", primary_header["OBJECT"])
    print("Filter:", primary_header["FILTER"])
    print("INSTRUME:", primary_header["INSTRUME"])
