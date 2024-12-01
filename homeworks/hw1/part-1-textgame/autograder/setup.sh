#!/usr/bin/env bash

apt-get install -y python3 python3-pip python3-dev

pip3 install -r /autograder/source/requirements.txt

pip3 install nbformat

pip3 install json

cd /autograder/source/CIS-7000/HW1

pip3 install .