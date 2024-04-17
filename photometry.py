from astropy.io import fits
import numpy as np
import argparse
from regions import Regions
from photutils.aperture import CircularAperture, aperture_photometry, ApertureStats
from astropy.stats import SigmaClip

bkg_clip_sigma = 3

ap = argparse.ArgumentParser(description='Applies aperture photometry to a series of images')
ap.add_argument("input_images", nargs="+", help="Input images from which to get fluxes", type=str)
ap.add_argument("-r", "--regions", nargs=1, help="Region file containing the apertures of the source for which to get fluxes from", type=str)
ap.add_argument("-b", "--background", nargs=1, help="Region file for the background", type=str)
ap.add_argument("-o", "--outname", nargs="?", help="Output file name", type=str, default=None)

args = ap.parse_args()

images = args.input_images
regions = args.regions[0]
background = args.background[0]
outname = "" if args.outname is None else args.outname
regions = Regions.read(regions, format="ds9")

bkg_reg = Regions.read(background, format="ds9")[0]
bkg_center = (bkg_reg.center.x, bkg_reg.center.y)
bkg_aperture = CircularAperture(bkg_center, r=bkg_reg.radius)
sigclip = SigmaClip(sigma=bkg_clip_sigma, maxiters=10)
source_rates = np.zeros((len(images), len(regions)))

for j, region in enumerate(regions):

    mjds = []
    rates= []
    errs = []
    exps = []

    for i, image in enumerate(images):
        print("Processing image: %s (%d/%d) with region %s" % (image, i, len(images), region.meta["text"]))
        imagefits = fits.open(image)
        imagedata = imagefits[0].data
        exptime = imagefits[0].header["EXPTIME"]
        mjd = imagefits[0].header["MJD-STRT"]
        filter = imagefits[0].header["FILTER"]
        # get background -- > Counts!
        phot_bkg = ApertureStats(imagedata, bkg_aperture, sigma_clip=sigclip)
        err_bkg = np.sqrt(phot_bkg.data_cutout) # poisson error

        source_center = (region.center.x, region.center.y)
        aperture = CircularAperture(source_center, r=region.radius)
        #counts
        phot_source = aperture_photometry(imagedata, aperture,
                       error=np.sqrt(imagedata), mask=np.isnan(np.sqrt(imagedata)))

        bkg_unc = np.sqrt(np.sum(err_bkg**2)) / phot_bkg.data_cutout.size * aperture.area # error on the mean
        source_net_counts = phot_source["aperture_sum"] - phot_bkg.median * aperture.area
        # add bkg uncertainty in quadrature
        source_net_err = np.sqrt(phot_source["aperture_sum_err"]**2 + bkg_unc**2)
        mjds.append(mjd)
        exps.append(exptime)
        rates.append(source_net_counts[0] / exptime)
        errs.append(source_net_err[0] / exptime)
    output = np.vstack((mjds, rates, errs, exps))
    np.savetxt(outname + "_" + region.meta["text"] + ".dat",output.T, header="mjd\trate\terr\texp")
