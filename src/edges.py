import rasterio
import numpy as np
import cv2

# path_to_tiff = r"/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-07-09..2024-07-10 0-1%/CLEANED 2024-07-09..2024-07-10 0-1%/2024-07-09..2024-07-10 T35UMA.tiff"
#
# with rasterio.open(path_to_tiff) as dataset:
#     band_index = 3
#     image = dataset.read(band_index).astype(np.uint8)
#
#     blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
#
#     edges = cv2.Canny(blurred_image, threshold1=250, threshold2=350)
#
#     output_path = "output_3.tiff"
#     with rasterio.open(
#         output_path,
#         "w",
#         driver="GTiff",
#         width=dataset.width,
#         height=dataset.height,
#         count=1,
#         dtype=edges.dtype,
#         crs=dataset.crs,
#         transform=dataset.transform,
#     ) as dst:
#         dst.write(edges, 1)
#
# print("Edges saved as GeoTIFF:", output_path)

import rasterio
import numpy as np
import cv2

# Read the TIFF file
path_to_tiff = r'/Users/juliusjancevicius/Desktop/Intelektualios_informacines_sistemos/data/2024-07-09..2024-07-10 0-1%/CLEANED 2024-07-09..2024-07-10 0-1%/2024-07-09..2024-07-10 T35UMA.tiff'
with rasterio.open(path_to_tiff) as dataset:
 # Read the image data for all bands (8 bands in my case)
 image = dataset.read()

# Convert image data to uint8
image = image.astype(np.uint8)

# Perform Canny edge detection on each band
edge_images = []
for band in image:
 edges = cv2.Canny(band, threshold1=200, threshold2=250) #again, keep in mind your threshold
 edge_images.append(edges)

# Combine the edge images into a single array
combined_edges = np.stack(edge_images, axis=0).astype("int16")

# Create a new GeoTIFF file for the combined edges
output_path = '/Users/juliusjancevicius/Desktop/2ND_Intelektualios/NEW_TEST/output2.tiff'
with rasterio.open(
 output_path,
 'w',
 driver='GTiff',
 width=dataset.width,
 height=dataset.height,
 count=combined_edges.shape[0],
 dtype=combined_edges.dtype,
 crs=dataset.crs,
 transform=dataset.transform,
) as dst:
 dst.write(combined_edges)

print("Combined edges saved:", output_path)
