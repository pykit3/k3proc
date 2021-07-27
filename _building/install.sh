#!/bin/sh


pwd="$(pwd)"
name="${pwd##*/}"
pip uninstall -y $name

cp setup.py ..
(
cd ..
python setup.py install
)
