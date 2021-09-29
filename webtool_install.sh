#! /bin/bash

echo 'Instalacja PIP'
apt install python3-pip
sleep 5
echo 'Instalacja bibliotek'
pip3 install tldextract pyfiglet
sleep 5
echo 'Można uruchomić WebTool - python3 webtool_x_x.py --h'
exit
