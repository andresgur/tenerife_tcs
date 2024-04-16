# tenerife-muscat2-tcs
Data reduction for the MUSCAT2 camera on the Telescopio Carlos Sanchez (TCS) on the Observatorio de Tenerife

The data needs to be stored into a single directory, with the flats and darks in separate directories. This is how a typical workflow would look like:

python reduce.py *.fits -f path/FLATS -d path/DARKS --> this will apply dark subtraction and flat fielding. The task already looks for the appropiate darks and flats based on the header exposure time and filters

./align_images.sh --> This will run aling_images.py and mean_images.py for each individual filter, thereby creating an aligned, stacked image of each filter. Then the filter stacks will be aligned.

You can then plot the images using:
python ~/scripts/tenerife/rgb_plot.py --red 0_*.fits --blue 1_*aligned.fits --green 2_*aligned.fits -p 1

Remember: python <script.py> -h will give you the input parameters and a small description of what the script does.
