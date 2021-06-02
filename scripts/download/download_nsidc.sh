#!/bin/bash
SOURCE=nsidc_sources.txt
DATA=data
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
              --reject "index.html*" \
              --reject "*.xml*" \
              --reject "*.PNG*" \
              --reject "*.PNT*" \
              --reject "*.jpg*" \
              --reject "*.png*" \
              -nH \
              -nc \
              $url; \
              sleep 1 ;
done <$SOURCE