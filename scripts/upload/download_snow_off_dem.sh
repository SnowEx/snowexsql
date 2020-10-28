#!/bin/bash
DEM_SOURCE=3DEP_sources_1m_DEM.txt
echo Downloading
DEM=~/Downloads/GM_DEM
echo $DEM
mkdir -p $DEM
while read img ; do \
        echo $img ; \
        wget -P $DEM -nc $img ; \
done <$DEM_SOURCE
