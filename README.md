# MODIS_Extraction
Code to extract MODIS imagery from NASA Earthdata repository. 

bands367_3031.xml: use to extract MODIS corrected surface reflectance imagery in coordinate reference systems (CRS) 3031- South Polar Steographic.

bands367_latlong.xml: Same as above but use to extract imagery in CRS 4326- WGS84 Lat/Long. 

The only values to change in the .xml files are the date (YYYY-MM-DD) and the MODIS product to download. Currently this is set to MODIS_Terra_CorrectedReflectance_Bands367 because these bands are well suited to discriminate between ice, cloud and water. Other MODIS data product codes can be found here: https://nasa-gibs.github.io/gibs-api-docs/available-visualizations/. 

Choose the 4326 CRS to allow the MODIS imagery to be directly overlaid on BSOSE/ ISO-SAF data without needing to reproject. 

The gdal_translate commands contained within the corresponding .sh files can be directly run in a shell script. The bounding box coordinates are currently set to extract imagery from the South Weddell Sea. 

