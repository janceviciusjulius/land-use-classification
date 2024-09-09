import numpy as np
import rasterio

# Open both rasters using rasterio
with rasterio.open("path_to_raster1.tif") as src1, rasterio.open("path_to_raster2.tif") as src2:
    # Read band 1 from both rasters (assuming im1b1 and im2b1 refer to the first bands)
    im1b1 = src1.read(1)
    im2b1 = src2.read(1)

    # Apply the conditional logic using NumPy
    result = np.where(
        (im2b1 == 1) | (im2b1 == 3) | (im2b1 == 8) | (im2b1 == 9) | (im2b1 == 10) | (im2b1 == 11),
        0,  # If condition is met, assign 0
        im1b1,  # Otherwise, keep the value from im1b1
    )

    # Define output profile using metadata from the first input raster
    output_profile = src1.profile
    output_profile.update(dtype=rasterio.float32)  # Adjust dtype if needed

    # Write the result to a new file
    with rasterio.open("path_to_output.tif", "w", **output_profile) as dst:
        dst.write(result, 1)  # Write the result to band 1
