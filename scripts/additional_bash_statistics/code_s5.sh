#!/usr/bin/env bash

grep -vF -e "https://drugst.one/?nodes=PTEN,TP53" -e "?trk"  -e '"https://drugst.one/?id="' $1  | awk '($7 ~ /[?&]id=/ || $7 ~ /[?&]nodes=/ || $7 ~ /\/standalone\?/) {print $1}'  | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort -u > $2