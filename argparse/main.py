"""

MODIS preprocess steps to enable incorproation into digital twin route planner.

Bin MODIS pixel values into categories 0-10 as a proxy for Sea Ice concentration (SIC)
Threshold pixels into cloud present (1) or absent (0)
Pool cloud and SIC image by user defined pool size
For every pixel create list of: lat_coordinate, lon_coordinate, date, SIC, cloud cover. 
Export list as NetCDF

"""


import numpy as np
from osgeo import gdal
import skimage.measure
import pandas as pd
import xarray as xr
import argparse

class CreateModisNetCDF():
    def __init__(self, input_im, output_netcdf, pool_size, dateTime):
        print('The pool size is {}'.format(pool_size))
        self.fn=str(input_im)
        self.ds = gdal.Open(self.fn)
        self.outfile=str(output_netcdf)
        self.pool_size=pool_size
        self.coordinateList=[]
        self.temporaryList=[]
        self.date=dateTime
        
        print('The date is {}'.format(self.date))

    

    def pixel2coord(self, row, col):
        
        """
        Convert row and column numbers to real-life coordinates using coordinate 
        reference system of original input image.
        
        returns
        
        ------
        xp, yp: x and y coordinates respectively for each pixel.
        
        """
        
        ul_x, res_x, distort_x, ul_y, distort_y, res_y = self.ds.GetGeoTransform()
        xp = (res_x*col)+ul_x
        yp = (res_y*row)+ul_y
        return xp, yp

    def createNetCDF(self):
        """
        Pool visible and swir (for cloud detection bands)
        Classify visible imagery into SIC bands, and cloud into present (1) and absent(0)
        Pass row and column value for every pixel into pixel2Coords() method to get
            coordinate for every pixel
        Generate list entry for every pixel with lat lon coordinate, date, SIC and cloud cover
        
        Generate netcdf of list for every coordinate
        
        
        Returns
        
        -----
        None
        
        """
        arr = self.ds.ReadAsArray()
        visible_band = arr[0, :, :]
        swir_band = arr[1, :, :]
        pool = self.pool_size

        cloudPooled = skimage.measure.block_reduce(swir_band, (pool, pool), np.mean)
        cloud_classified = np.where(cloudPooled > 130, 1, 0)
        
        ice_pooled = skimage.measure.block_reduce(visible_band, (pool, pool), np.mean)

        classify=np.where(visible_band<25, 1, np.where((visible_band>25)&(visible_band<51), 2,
                                     np.where((visible_band>51)&(visible_band<76), 3,
                                     np.where((visible_band>76)&(visible_band<101), 4, 
                                     np.where((visible_band>101)&(visible_band<127), 5,
                                     np.where((visible_band>127)&(visible_band<152), 6,
                                     np.where((visible_band>152)&(visible_band<177), 7, 
                                     np.where((visible_band>177)&(visible_band<203), 8,
                                     np.where((visible_band>203)&(visible_band<229), 9,10)))))))))
        
        
        
        classifyPooled=np.where(ice_pooled<25, 1, np.where((ice_pooled>25)&(ice_pooled<51), 2, 
                                     np.where((ice_pooled>51)&(ice_pooled<76), 3,
                                     np.where((ice_pooled>76)&(ice_pooled<101), 4, 
                                     np.where((ice_pooled>101)&(ice_pooled<127), 5,
                                     np.where((ice_pooled>127)&(ice_pooled<152), 6,
                                     np.where((ice_pooled>152)&(ice_pooled<177), 7, 
                                     np.where((ice_pooled>177)&(ice_pooled<203), 8,
                                     np.where((ice_pooled>203)&(ice_pooled<229), 9,10)))))))))

        coordinateList = self.coordinateList
        listTemp = self.temporaryList
        for i in range(classifyPooled.shape[0]):
            for j in range(classifyPooled.shape[1]):
                outCoord = a.pixel2coord((i*pool), (j*pool))
                outVal = classifyPooled[i, j]/10.
                cloudVal = cloud_classified[i, j]
                time = self.date
                listTemp = [outCoord[0], outCoord[1], time, outVal, cloudVal]
                coordinateList.append(listTemp)

        df = pd.DataFrame(coordinateList)
        df.columns = ["long", "lat", "time", "iceArea", "cloud"]
        df = df[["long", "lat", "time", "iceArea", "cloud"]]
        df = df.set_index(["long", "lat", "time"])
        ncdf = xr.Dataset.from_dataframe(df)
        outfile = self.outfile
        print("Saving to file:", outfile)
        ncdf.to_netcdf(outfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_image", "-i", type=str)
    parser.add_argument("--output_netcdf", "-o", type=str)
    parser.add_argument("--pool_size", "-p", default=1, type=int)
    parser.add_argument("--image_date", "-d", default="2021-01-01", type=str)
    args = parser.parse_args()
    
    a=CreateModisNetCDF(args.input_image, args.output_netcdf, args.pool_size, args.image_date)
    a.createNetCDF()
