# @Author: Andrés Gúrpide <agurpide>
# @Date:   04-16-2023
# @Email:  a.gurpide-lasheras@soton.ac.uk
# @Last modified by:   agurpide
# @Last modified time: 04-16-2024
from astropy.io import fits
import argparse
import glob

ap = argparse.ArgumentParser(description='List of images for which the header needs to be fixed')
ap.add_argument("input_images", nargs=1, help="Input images to be inspected", type=str)
args = ap.parse_args()

images = glob.glob(args.input_images[0])
for i, image in enumerate(images):
    print("Processing image: %s (%d/%d)" % (image, i + 1, len(images)))
    imagefits = fits.open(image)
    date = imagefits[0].header["DATE-OBS"]
    y,m,d = date.split("-")
    y = int(y)
    m = int(m)
    d = int(d)
    newymd = "%d-%02d-%02d" % (y,m,d)
    imagefits[0].header["DATE-OBS"] = newymd
    imagefits[0].header['TIMEOBS'] = imagefits[0].header['EXP-STRT']
    imagefits.writeto(image.replace('.fits','_fixed.fits'), overwrite=True)
    imagefits.close()
