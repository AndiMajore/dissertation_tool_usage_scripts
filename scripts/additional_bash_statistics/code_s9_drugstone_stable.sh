#!/usr/bin/env bash
cat ../logs/$1/*-access-filtered.log |  awk '{print $1}' | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort -u > ../results/$1_unique_part.ips
cat ../logs/drugstone/cdn-access-filtered.log | grep "stable" |  awk '{print $1}' | grep -oE "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" | sort -u >> ../results/$1_unique_part.ips
cat ../results/$1_unique_part.ips | sort -u > ../results/$1_unique.ips
rm ../results/$1_unique_part.ips