#!/usr/bin/env bash
rm -rfv ./venv/
virtualenv ./venv
source ./venv/bin/activate
pip install -r ./requirements.txt --upgrade
