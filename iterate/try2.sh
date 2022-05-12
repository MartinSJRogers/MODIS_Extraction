#!bin/bash
while read -r ARGSTR; do
  FILENAME=`echo $ARGSTR | awk -F, '{ print $2 }'`
  echo $FILENAME
  COORD_1=`echo $ARGSTR | awk -F, '{ print $3}'`
  COORD_2=`echo $ARGSTR | awk -F, '{ print $4}'`
  COORD_3=`echo $ARGSTR | awk -F, '{ print $5}'`
  COORD_4=`echo $ARGSTR | awk -F, '{ print $6}'`
  DATE=`echo $ARGSTR | awk -F, '{print $1}'`
  echo $DATE
  echo $COORD_1
  sed -r 's/DATE/$DATE/g' bands367_3031.xml >template.xml
  gdal_translate -of GTiff -projwin $COORD_1 $COORD_2 $COORD_3 $COORD_4 bands367_3031.xml $FILENAME
done < coords.txt