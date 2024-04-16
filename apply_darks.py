from astropy.io import fits
import numpy as np
import argparse
import astroalign as aa
from astropy import stats
import matplotlib.pyplot as plt
from astropy import stats
import glob
import matplotlib.pyplot as plt

sigclip = stats.SigmaClip(sigma=4, maxiters=5)

def create_master_dark(exptime, filter):
    """Creates master dark given a exposure time and filter"""
    print("Creating master dark for exp: %.1f and %s filter" % (exptime, filter))
    darks = []

    for darkfile in darkfiles:
        darkfits = fits.open(darkfile)
        darkexptime = darkfits[0].header["EXPTIME"]
        darkfilter = darkfits[0].header["FILTER"]
        if (darkexptime == exptime) & (darkfilter == filter):
            darks.append(darkfits[0].data)
    if len(darks)==0:
        raise ValueError("No darks were found!")
    print("Found %d dark files" % len(darks))
    masterdark = np.mean(sigclip(darks, axis=0), axis=0)
    return masterdark

ap = argparse.ArgumentParser(description='Apply dark subtraction to science images')
ap.add_argument("input_images", nargs="+", help="Input images to be dark-subtracted", type=str)
ap.add_argument("-d", "--dark_folder", nargs=1, help="Folder containing the darks", type=str)

args = ap.parse_args()

images = args.input_images

darkfolder = args.dark_folder[0]

darkfiles = glob.glob("%s/MCT2*.fits" % darkfolder)
print("Found %d dark files in total" % len(darkfiles))

for i, image in enumerate(images):
    print("Processing image: %s (%d/%d)" % (image, i, len(images)))
    current_fits = fits.open(image)
    current_data = current_fits[0].data
    exptime = current_fits[0].header["EXPTIME"]
    filter = current_fits[0].header["FILTER"]
    masterdark = create_master_dark(exptime, filter)
    cleandata = current_data - masterdark.data
    cleandata[np.isnan(masterdark)] = np.nan
    current_fits[0].data = cleandata
    current_fits[0].header["COMMENT"] = "Dark subtracted"
    current_fits.writeto(image.replace(".fits", "_darksubtracted.fits"), overwrite=True)
