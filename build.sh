#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
pip install -e .
firstlight init-db
