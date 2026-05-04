#!/usr/bin/env bash
cat ../logs/$1/*-access-filtered.log | awk '{print $1}' | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort -u > ../results/$1_unique.ips