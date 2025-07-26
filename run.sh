#!/bin/bash

# Activate the virtual environment
source "$(dirname "$0")/venv/bin/activate"

# Run the API Checker
python "$(dirname "$0")/api_checker.py" "$@"
