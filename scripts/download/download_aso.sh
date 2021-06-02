#!/bin/bash
SOURCE=aso_sources.txt
DATA=data/aso
mkdir -p $DATA
while read url ; do \
        echo Downloading $url ; \
        wget --load-cookies ~/.urs_cookies \
              --save-cookies ~/.urs_cookies \
              --keep-session-cookies \
              --no-check-certificate \
              --auth-no-challenge=on \
              -np \
              -P $DATA \
              -e robots=off \
              --recursive \
              -nH \
              -nc \
              $url; \
              sleep 1 ;
done <$SOURCE

# Unzip
find . -name "*.zip" | while read filename; do unzip -o -d "`dirname "$filename"`" "$filename"; done;

# Reproject the files into the NAD 83 from WGS84
REPROJECTED=$DATA/reprojected
mkdir -p $REPROJECTED

# Reproject the Colorado files
CO_FILES=$(find $DATA/USCO -type f -name "*swe*.tif" -o -name "*_snowdepth*.tif")

# Reproject Colorado Files
for f in $CO_FILES
  do
    echo "Reprojecting $f from 32612 to 26912"
    out=$(basename $f)
    gdalwarp -t_srs EPSG:26912 -r bilinear $f "$REPROJECTED/$out"
  done

# TODO: Unsurpress the ID files for projection
# ID_FILES=$(find $DATA/USID -type f -name "*swe*.tif" -o -name "*_snowdepth*.tif")
#for f in $ID_FILES
#  do
#    echo "Reprojecting $f from 32611 to 26911"
#    out=$(basename $f)
#    gdalwarp -t_srs EPSG:26911 -r bilinear $f "$REPROJECTED/$out"
#  done