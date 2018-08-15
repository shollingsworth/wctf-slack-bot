#!/usr/bin/env bash
source <(./env_setup/get_env.py dev)
export FLASK_APP=main.py
export FLASK_DEBUG=1
source ./venv/bin/activate
python -m flask run
