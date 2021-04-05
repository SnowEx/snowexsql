#!/bin/bash
SOURCE=nsidc_sources.txt
echo Downloading
DATA=data
mkdir -p $DATA
while read url ; do \
        echo $url ; \
        wget --load-cookies ~/.urs_cookies \
              --save-cookies ~/.urs_cookies \
              --keep-session-cookies \
              --no-check-certificate \
              --auth-no-challenge=on \
              --reject "index.html*" \
              -np \
              -P $DATA \
              -e robots=off \
              -nc \
              $url; \
done <$SOURCE