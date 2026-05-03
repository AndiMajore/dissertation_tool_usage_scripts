#!/usr/bin/env bash

cd scripts
python3 combine.py
python3 separate_apps_tools_and_pseudonymize.py
python3 clean_logs.py
python3 statistics.py
python3 additional_statistics.py