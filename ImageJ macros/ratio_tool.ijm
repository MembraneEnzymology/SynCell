macro "Ratio Action Tool - C000C800C080C880C008C808C088D25D26D27D34D35D38D39D3aD43D44D45D47D48D49D4aD4bD52D53D54D56D57D58D59D5aD5bD61D62D63D64D66D67D68D69D6aD6bD6cD71D72D73D74D76D77D78D79D7aD7bD7cD81D82D83D84D86D87D88D89D8aD8bD8cD91D92D93D94D96D97D98D99D9aD9bD9cDa1Da2Da3Da4Da6Da7Da8Da9DaaDabDb1Db2Db3Db4Dc2Dc3Dc4Dc5Dc6Dc7Dc8Dc9DcaDcbDd2Dd3Dd4Dd5Dd6Dd7Dd8Dd9DdaDdbDe3De4De5De6De7De8De9DeaDf5Df6Df7Df8C888CcccCf00D28D29D2aD2bD36D37D3bD3cD46D4dD4eD55D5eD65D6eD75D7eD85D8eD95D9dD9eDa5DacDadDb5Db6Db7Db8Db9DbaDbbDbcC0f0Cff0C00fCf0fC0ff"{
	
	getDimensions(width, height, channels, slices, frames);
	run("Set Measurements...", "mean redirect=None decimal=3");
	
	title = getTitle();
	
	// skip last frame!!!
	for (frame = 1; frame < frames; frame++) {
		Stack.setPosition(1, 1, frame);
		List.setMeasurements;
		mean1 = parseFloat(List.get("Mean"));
		x = parseFloat(List.get("X"));
		y = parseFloat(List.get("Y"));
		
		Stack.setPosition(3, 1, frame);
		List.setMeasurements;
		mean2 = parseFloat(List.get("Mean"));
		
		ratio = mean1 / mean2;
		
		row = nResults;
		setResult("filename", row, title);
		setResult("frame", row, frame);
		setResult("x", row, x);
		setResult("y", row, y);
		setResult("mean_channel1", row, mean1);
		setResult("mean_channel3", row, mean2);
		setResult("ratio", row, mean2 / mean1);
	}
	
}
