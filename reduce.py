from astropy.io import fits
import numpy as np
import argparse
import astroalign as aa
from astropy import stats
import matplotlib.pyplot as plt
from astropy import stats
import glob
import matplotlib.pyplot as plt
from multiprocessing import Pool

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

def create_master_flat(filter):
    """Creates master flat given a exposure time and filter"""
    print("Creating master flat for %s filter" % (filter))

    flats = []

    for flatfile in flatfiles:
        flatfits = fits.open(flatfile)
        flatfilter = flatfits[0].header["FILTER"]
        if (flatfilter == filter):
            flats.append(flatfits[0].data)

    if len(flats)==0:
        raise ValueError("No flats were found!")
    print("Found %d flats files" % len(flats))
    masterflat = np.mean(sigclip(flats, axis=0), axis=0)
    # renormalize the flat at the end
    return masterflat / np.mean(masterflat)

def cleanimage(image):
    current_fits = fits.open(image)
    current_data = current_fits[0].data
    exptime = current_fits[0].header["EXPTIME"]
    filter = current_fits[0].header["FILTER"]
    masterdark = create_master_dark(exptime, filter)
    cleandata = current_data - masterdark.data
    masterflat = create_master_flat(filter)
    normalized_data = cleandata / masterflat.data
    normalized_data[np.isnan(masterflat)] = np.nan
    current_fits[0].data = normalized_data
    current_fits[0].header["COMMENT"] = "Dark subtracted"
    current_fits[0].header["COMMENT"] = "Flat Normalized"
    current_fits.writeto(image.replace(".fits", "_clean.fits"), overwrite=True)

ap = argparse.ArgumentParser(description='Apply flat correction to a series of science images')
ap.add_argument("input_images", nargs="+", help="Input images to be flat-normalized", type=str)
ap.add_argument("-f", "--flat_folder", nargs=1, help="Folder containing the flats", type=str)
ap.add_argument("-d", "--dark_folder", nargs=1, help="Folder containing the darks", type=str)
args = ap.parse_args()

images = args.input_images

flatfolder = args.flat_folder[0]

flatfiles = glob.glob("%s/MCT2*.fits" % flatfolder)
print("Found %d flat files in total" % len(flatfiles))

darkfolder = args.dark_folder[0]
darkfiles = glob.glob("%s/MCT2*.fits" % darkfolder)
print("Found %d dark files in total" % len(darkfiles))

with Pool(14) as p:
    p.map(cleanimage, images)
if False:
    for i, image in enumerate(images):

        current_fits = fits.open(image)
        current_data = current_fits[0].data
        exptime = current_fits[0].header["EXPTIME"]
        filter = current_fits[0].header["FILTER"]
        masterdark = create_master_dark(exptime, filter)
        cleandata = current_data - masterdark.data
        masterflat = create_master_flat(filter)
        normalized_data = cleandata /  masterflat.data
        normalized_data[np.isnan(masterflat)] = np.nan
        current_fits[0].data = normalized_data
        current_fits[0].header["COMMENT"] = "Dark subtracted"
        current_fits[0].header["COMMENT"] = "Flat Normalized"
        current_fits.writeto(image.replace(".fits", "_clean.fits"), overwrite=True)
