from astropy.io import fits
import numpy as np
import argparse
import astroalign as aa
from astropy import stats
import matplotlib.pyplot as plt

sigclip = stats.SigmaClip(sigma=4, maxiters=5)

ap = argparse.ArgumentParser(description='Make a mean image out of a list of images')
ap.add_argument("input_images", nargs="+", help="Input images to be inspected", type=str)
ap.add_argument("-o", "--outputname", nargs="?", help="Output file name",
                type=str, default=None)
args = ap.parse_args()

images = args.input_images

outputfilename = args.outputname

alldata = []
exposuretime = 0
for i, image in enumerate(images):
    print("Processing %d/%d" % (i, len(images)))
    current_fits = fits.open(image)
    current_data = current_fits[0].data
    alldata.append(current_data)
    exposuretime += current_fits[0].header["EXPTIME"]
    object = current_fits[0].header["OBJECT"]

filtereddata = np.mean(sigclip(alldata, axis=0), axis=0)

current_fits[0].header["EXPTIME"] = exposuretime
if outputfilename is None:
    outname = "%s_%s_%d.fits" % ("stacked", object, len(images))
else:
    outname = "%s_%s_%d.fits" % (outputfilename, object, len(images))

current_fits.writeto(outname, overwrite=True)

print("Stacked stored to %s" % outname)
#current_fits.writeto(image.replace(".fits", "_aligned.fits"), overwrite=True)
