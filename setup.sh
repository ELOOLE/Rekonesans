#! /bin/bash

echo 'Instalacja PIP'
apt install python3-pip
sleep 5
echo 'Instalacja bibliotek'
pip install json2html
sleep 5
pip install pyfiglet
sleep 5
pip install selenium
sleep 5
pip install bs4
sleep 5
pip install impacket
sleep 5
pip install Pillow
sleep 5
echo 'Można już uruchomić'
exit