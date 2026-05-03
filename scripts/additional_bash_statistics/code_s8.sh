#!/usr/bin/env bash

grep "drugstone.js" $1 |  awk '{print $1}' | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort -u > $2