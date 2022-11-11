import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import rasterstats
from rasterstats import zonal_stats

path_2004ag = "./Lab2_data/data/agriculture/GLOBCOVER_2004_lab2.tif"
path_2009ag = "./Lab2_data/data/agriculture/GLOBCOVER_2009_lab2.tif"

temp_list =[]
text01_list =[]
with open('./Lab2_data/data/districts/district01.txt') as f:
    for coordinates in f:
        temp_list = tuple(coordinates.strip().split('\t'))
        text01_list.append(temp_list)    
    
temp_list =[]
text05_list =[]
with open('./Lab2_data/data/districts/district05.txt') as f:
    for coordinates in f:
        temp_list = tuple(coordinates.strip().split('\t'))
        text05_list.append(temp_list)
        
temp_list =[]
text06_list =[]
with open('./Lab2_data/data/districts/district06.txt') as f:
    for coordinates in f:
        temp_list = tuple(coordinates.strip().split('\t'))
        text06_list.append(temp_list)

new_text01 = []
for index in text01_list:
   my_temp = []
   for element in index:
      if element.isalpha():
         my_temp.append(element)
      else:
         my_temp.append(float(element))
   new_text01.append((my_temp[0],my_temp[1]))

new_text05 = []
for index in text05_list:
   my_temp = []
   for element in index:
      if element.isalpha():
         my_temp.append(element)
      else:
         my_temp.append(float(element))
   new_text05.append((my_temp[0],my_temp[1]))

new_text06 = []
for index in text06_list:
   my_temp = []
   for element in index:
      if element.isalpha():
         my_temp.append(element)
      else:
         my_temp.append(float(element))
   new_text06.append((my_temp[0],my_temp[1]))

for newdel in [new_text01, new_text05, new_text06]:
    del newdel[0]

poly_text01 = Polygon(new_text01)
poly_text05 = Polygon(new_text05)
poly_text06 = Polygon(new_text06)

dist01_df = pd.DataFrame(new_text01, columns=['Longitude', 'Latitude'])
dist05_df = pd.DataFrame(new_text05, columns=['Longitude', 'Latitude'])
dist06_df = pd.DataFrame(new_text06, columns=['Longitude', 'Latitude'])

gdf01 = gpd.GeoDataFrame(dist01_df, geometry=gpd.points_from_xy(dist01_df.Longitude, dist01_df.Latitude))
gdf05 = gpd.GeoDataFrame(dist05_df, geometry=gpd.points_from_xy(dist05_df.Longitude, dist05_df.Latitude))
gdf06 = gpd.GeoDataFrame(dist06_df, geometry=gpd.points_from_xy(dist06_df.Longitude, dist06_df.Latitude))
 
gdf01.insert(3, 'district', '01')
gdf05.insert(3, 'district', '05')
gdf06.insert(3, 'district', '06')

for gdf in [gdf01, gdf05, gdf06]:
    gdf.insert(4, 'num_coords', len(gdf.axes[0]))

zonal_d01 = zonal_stats(poly_text01, path_2004ag, categorical = True)
zonal_d05 = zonal_stats(poly_text05, path_2004ag, categorical = True)
zonal_d06 = zonal_stats(poly_text06, path_2004ag, categorical = True)

zonal_d0109 = zonal_stats(poly_text01, path_2009ag, categorical = True)
zonal_d0509 = zonal_stats(poly_text05, path_2009ag, categorical = True)
zonal_d0609 = zonal_stats(poly_text06, path_2009ag, categorical = True)

ag_04 = []
list_overall = []
for district in [zonal_d01, zonal_d05, zonal_d06]:
    dist_dict = district[0]
    dist_ag = dist_dict.get(1)
    dist_overall = dist_dict.get(0)
    ag_percent = str(round(((dist_ag / (dist_overall + dist_ag)) * 100), 2))
    ag_04.append(ag_percent)

ag_09 = []
list_overall = []
for district in [zonal_d0109, zonal_d0509, zonal_d0609]:
    dist_dict = district[0]
    dist_ag = dist_dict.get(1)
    dist_overall = dist_dict.get(0)
    ag_percent = str(round(((dist_ag / (dist_overall + dist_ag)) * 100), 2))
    ag_09.append(ag_percent)


print ("The percent of agricultural land in districts 01, 05, & 06 in 2004 was: " + ag_04[0] + "%, " + ag_04[1] + "%, and" + ag_04[2])
print ("The percent of agricultural land in districts 01, 05, & 06 in 2009 was: " + ag_09[0] + "%, " + ag_09[1] + "%, and" + ag_09[2])


