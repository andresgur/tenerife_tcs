from astropy.io import fits
import numpy as np
import argparse
import astroalign as aa

aa.PIXEL_TOL = 15
#aa.NUM_NEAREST_NEIGHBORS =
aa.MIN_MATCHES_FRACTION = 0.8
aa.NUM_NEAREST_NEIGHBORS = 7
ap = argparse.ArgumentParser(description='Align a set of images to a reference image')
ap.add_argument("input_images", nargs="+", help="Input images to be aligned", type=str)
ap.add_argument("-r", "--ref_image", nargs=1, help="Reference image to which align all images", type=str)
args = ap.parse_args()

ref_image = args.ref_image[0]

print("Reference image: %s" % ref_image)

target = fits.open(ref_image)[0].data
target_fixed = np.array(target, dtype="<f4")

images = args.input_images

for i, image in enumerate(images):
    print("Processing image: %s (%d/%d)" % (image, i, len(images)))
    if image==ref_image:
        print("Skipping reference image")
        continue
    current_fits = fits.open(image)
    source = current_fits[0]
    source_fixed = np.array(source.data, dtype="<f4")
    try:
        registered_image, footprint = aa.register(source_fixed,
                                              target_fixed,
                                              detection_sigma=4)
    except aa.MaxIterError as e:
        print(e)
        print("Failed on image  %s (%d/%d)" % (image, i, len(images)))
        continue
    registered_image[footprint] = np.nan
    current_fits[0].data = registered_image
    current_fits[0].header["COMMENT"] = "Aligned to %s" % ref_image
    current_fits.writeto(image.replace(".fits", "_aligned.fits"), overwrite=True)
