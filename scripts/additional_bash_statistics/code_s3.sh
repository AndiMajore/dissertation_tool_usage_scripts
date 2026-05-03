#!/usr/bin/env bash

grep -vF -e "https://drugst.one/?nodes=PTEN,TP53" -e "?trk"  -e '"https://drugst.one/?id="' $1  | awk '($7 ~ /[?&]id=/ || $7 ~ /[?&]nodes=/ || $7 ~ /\/standalone\?/) {print $11}'  | tr -d '"'  | awk '{ split($1, a, "/"); gsub(/^www\./, "", a[3]); print a[3] }' | awk '$1 ~ /\.[a-zA-Z]/'  | sort -u | wc -l