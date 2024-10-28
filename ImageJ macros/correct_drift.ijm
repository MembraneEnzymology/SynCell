drift_max = 30;

setBatchMode(true);

id = getImageID();
Roi.getBounds(roi_x, roi_y, roi_width, roi_height);
Stack.getDimensions(width, height, channels, slices, frames);
Stack.getPosition(channel, slice, frame);

run("FFT");
rename("fft1");


roi_x_start = roi_x;
roi_y_start = roi_y;
run("Clear Results");

for (f = frame + 1; f <= frames; f++) {

	
	selectImage(id);
	Stack.setPosition(2, 1, f);
	makeRectangle(roi_x, roi_y, roi_width, roi_height);
	
	run("FFT");
	rename("fft2");
	
	run("FD Math...", "image1=fft1 operation=Correlate image2=fft2 result=corr do");
	close("fft2");
	
	selectImage("corr");
	cx = getWidth() / 2;
	cy = getHeight() / 2;
	x_max = cx;
	y_max = cy;
	value_max = getPixel(x_max, y_max);
	
	for (y = 0; y <= getHeight; y++) {
		for (x = 0; x <= getWidth; x++) {
			value = getPixel(x, y);
			if (value > value_max) {
				value_max = value;
				x_max = x;
				y_max = y;

			}
		}
	}
	
	close("corr");
	
	drift_x = x_max - cx;
	drift_y = y_max - cy;
	
	if (abs(drift_x) < drift_max && abs(drift_y) < drift_max) {
		roi_x -= drift_x;
		roi_y -= drift_y;
	}

	row = nResults;
	setResult("frame", row, f);
	setResult("dx", row, roi_x_start - roi_x);
	setResult("dy", row, roi_y_start - roi_y);
	
}

close("fft2");

selectImage(id);
run("Select None");

// correct drift
for (row = 0; row < nResults; row++) {
	showProgress(row, nResults);
	
	f = getResult("frame", row);
	dx = getResult("dx", row);
	dy = getResult("dy", row);
	
	for (channel = 1; channel <= 3; channel++) {
		Stack.setPosition(channel, 1, f);
		run("Translate...", "x=&dx y=&dy interpolation=None slice");
	}
}

setBatchMode(false);