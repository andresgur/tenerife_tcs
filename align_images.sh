for filter in 0 1 2 3
	do printf "Aligning filter $filter\n"
	filterimages=$(ls MCT2$filter\_*_clean.fits)
	firstimage=$(ls MCT2$filter\_*_clean.fits | head -n 1)
	python ~/scripts/tenerife/align_images.py $filterimages -r $firstimage
	alignedimages=$(ls MCT2$filter\_*_clean_aligned.fits)
	printf "Creating stack for filter $filter\n"
	python ~/scripts/tenerife/mean_images.py $alignedimages -o $filter	
done

# align the three filters
python ~/scripts/tenerife/align_images.py 1_*[^d].fits 2_*[^d].fits 3_*[^d].fits -r 0_*[^d].fits
printf "python ~/scripts/tenerife/rgb_plot.py --red 0_*.fits --blue 1_*aligned.fits --green 2_*aligned.fits -p 1"
