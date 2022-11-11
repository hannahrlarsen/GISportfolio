import numpy as np
import rasterio
import numpy.ma as ma
import pandas as pd
from scipy.spatial import cKDTree
from rasterio.warp import reproject, Resampling, calculate_default_transform

path = '/Users/hannahlarsen/Desktop/UC Denver/FA 2022/Python and GIS/Lab4_data/'


def raster_reproject(raster_file):
    #This function reprojects raster files into the WGS 1984 projection
    #The input is a path using rasterio.open(path) that takes the form of
    #raster_reproject(rasterio.open(path))
    
    srcRst = raster_file
    dstCrs = 'EPSG: 4326'
    
    transform, width, height = calculate_default_transform(srcRst.crs, dstCrs, 
                                srcRst.width, srcRst.height, *srcRst.bounds)
    kwargs = srcRst.meta.copy()
    kwargs.update({'crs': dstCrs, 'transform': transform, 
                   'width': width, 'height': height})
    destination = np.zeros((1765, 1121), np.uint8)
    
    for i in range(1, srcRst.count + 1):
        reproject(source = rasterio.band(srcRst, i), 
                  destination = destination, src_crs = srcRst.crs, 
                  dst_crs = dstCrs, resampling = Resampling.nearest)
        return destination
    
    
def mean_filter(ma, mask):
    """Calculates a moving window average on a given array ma. The windows are 
defined by the mask.
    Example: for a moving window of size 10 by 10, mask will need to be an array of
10 rows by 10 columns
    Args:
        ma (numpy.ndarray): Array which the moving window will be applied to
        mask (numpy.ndarray): Mask that defines the window size 
    Returns:
        numpy.ndarray: Averaged array of same size as input array ma
    """
    pct_array = np.zeros(ma.shape)
    win_area = float(mask.sum())
    row_dim = mask.shape[0]//2
    col_dim = mask.shape[1]//2
    for row in range(row_dim,ma.shape[0]-row_dim):
        for col in range(col_dim,ma.shape[1]-col_dim):
            win = ma[row-row_dim:row+row_dim+1,col-col_dim:col+col_dim+1]
            pct_array[row,col] = win.sum()
    return pct_array/win_area


urban = raster_reproject(rasterio.open(path + 'urban_areas.tif'))
urban_new = np.where(urban < 0, 0, urban)

water = raster_reproject(rasterio.open(path + 'water_bodies.tif'))
water_new = np.where(water < 0, 0, water)

protected = raster_reproject(rasterio.open(path + 'protected_areas.tif'))
protected_new = np.where(protected < 0, 0, protected)

slope = raster_reproject(rasterio.open(path + 'slope.tif'))
slope_new = np.where(slope < 0, 0, slope)

wind = raster_reproject(rasterio.open(path + 'ws80m.tif'))
wind_new = np.where(wind < 0, 0, wind)


indexer = np.arange(11)[None, :] + 2*np.arange(9)[:, None]

urban_moving = mean_filter(urban_new, indexer) 
urban_arr = ma.masked_less(urban_moving, 0)

water_moving = mean_filter(water_new, indexer)
water_arr = ma.masked_less(water_moving, 0.02)

protected_moving = mean_filter(protected_new, indexer)
protected_arr = ma.masked_less(protected_moving, 0.05)


slope_moving = mean_filter(slope_new, indexer)
slope_arr = ma.masked_less(slope_moving, 15)


wind_moving = mean_filter(wind_new, indexer)
wind_arr = ma.masked_greater(wind_moving, 8.5)


urbanint = np.where(urban_arr, 1, 0)
waterint = np.where(water_arr, 1, 0)
protectedint = np.where(protected_arr, 1, 0)
slopeint = np.where(slope_arr, 1, 0)
windint = np.where(wind_arr, 1, 0)

final = urbanint + waterint + slopeint + protectedint + windint
count = (final == 5).sum()

print("The number of sites that have a value of 5 are: " + str(count))

with rasterio.open(path + 'urban_areas.tif') as src:
    ras_meta = src.profile

with rasterio.open(path + 'final_raster.tif', 'w', **ras_meta) as dst:
    dst.write(final, indexes = 1)
    

final_raster = rasterio.open(path + 'final_raster.tif')
final_raster.transform

cell_size = final_raster.transform[0]

x = final_raster.bounds[0] + (cell_size / 2)
y = final_raster.bounds[3] - (cell_size / 2)

bounds = final_raster.bounds

x_coords = np.arange(bounds[0] + cell_size/2, bounds[2], cell_size)
y_coords = np.arange(bounds[1] + cell_size/2, bounds[3], cell_size)


x, y = np.meshgrid(x_coords, y_coords)

coords_raster = np.c_[x.flatten(), y.flatten()]

points = pd.read_csv(path + 'transmission_stations.txt')


coords_raster_v = np.vstack([x.flatten(),y.flatten()])
coords_raster = coords_raster_v.T
tree = cKDTree(points)
distance, indexes = tree.query(coords_raster)

print('The maximum distance between a suitable site and transmission station is:', 
      round(distance.max(), 2))
print('The minimum distance between a suitable site and transmission station is:', 
      round(distance.min(), 2))

