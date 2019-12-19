#!/bin/sh
rm -rf vendor
mkdir vendor
pip install --target ./vendor requests
