import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import argparse
from matplotlib.colors import LogNorm

def scale(data):
    data = data / (np.nanmax(data))
    scale_max = np.nanpercentile(data, 100 - percentile)
    scale_min = np.nanpercentile(data, percentile)
    imageData = np.clip(data, scale_min, scale_max)
    imageData = (imageData - scale_min) / (scale_max - scale_min)
    #data[data < low] = low
    return imageData

ap = argparse.ArgumentParser(description='Create RGB image')
ap.add_argument("-r", "--red", nargs=1, help="Image for red channel", type=str)
ap.add_argument("-b", "--blue", nargs=1, help="Image for blue channel", type=str)
ap.add_argument("-g", "--green", nargs=1, help="Image for green channel", type=str)
ap.add_argument("-p", "--percentile", nargs="?", default=0.05, help="Percentile for the normalization", type=float)
args = ap.parse_args()

red = args.red[0]
blue = args.blue[0]
green = args.green[0]

percentile = args.percentile

redfits = fits.open(red)
bluefits = fits.open(blue)
greenfits = fits.open(green)

for fits in [redfits, bluefits, greenfits]:
    pixels = np.isnan(fits[0].data)
    #for fits2 in [redfits, bluefits, greenfits]:
    #    fits2[0].data[pixels] = 0

imgs = []
for fits in [redfits, greenfits, bluefits]:
    imgs.append(scale(fits[0].data))

imgs = np.array(imgs)
fig = plt.figure()

plt.title(greenfits[0].header["OBJECT"])
plt.imshow(np.transpose(imgs, axes=(1, 2, 0)),
            origin="lower")#norm=LogNorm(vmin=0.1, vmax=0.99))

outname = greenfits[0].header["OBJECT"]
print("Plot stored to %s_rgb.png" % outname)
plt.gca().get_xaxis().set_visible(False)
plt.gca().get_yaxis().set_visible(False)
plt.savefig("%s_rgb.png" % outname, dpi=500, bbox_inches="tight", pad_inches = 0.05)
