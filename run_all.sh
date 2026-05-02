#!/usr/bin/env bash

cd scripts
python3 combine.py
python3 separate_apps_tools_and_pseudonomize.py
python3 clean_logs.py
python3 statistics.py