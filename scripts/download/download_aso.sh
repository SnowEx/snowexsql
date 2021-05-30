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
find . -name "*.zip" | while read filename; do unzip -o -d "`dirname "$filename"`" "$filename"; done;
