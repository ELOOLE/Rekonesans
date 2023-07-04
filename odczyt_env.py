#!/usr/bin/env python

import datetime
import subprocess
from sys import argv
import os.path
import argparse
import shodan
import sys
import time
import pyfiglet
import re
import socket
import shlex, subprocess, signal

def f_odczyt_pliku(plik):
    uchwyt_pliku = open(plik, 'r')
    i = 0
    
    adres = []

    for line in uchwyt_pliku:
        adres = line.split("|")
        
        f_zapisz_wynik_do_pliku(plik_z_wynikiem, "-------------------------------------------------------------------------------------------" + os.linesep)
        for dane in adres:
            f_zapisz_wynik_do_pliku(plik_z_wynikiem, dane + os.linesep)
        
        cmd = f"curl -kI {adres[0]} "
        wget_output = f_polecenie_uniwersalne("curl", cmd)

        f_zapisz_wynik_do_pliku(plik_z_wynikiem, "-------------------------------------------------------------------------------------------" + os.linesep)

        #print(f"0 {adres[0]}")

    uchwyt_pliku.close()

def f_polecenie_uniwersalne(polecenie, cmd):
    # zapisuje do logu wykonane polecenie
    ps = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    
    try:
        output, errs = ps.communicate(timeout=20)
        #output = f_trim_output(output) 
            
        # zapisuje do logu wynik polecenia
        f_zapisz_wynik_do_pliku(plik_z_wynikiem, f"{polecenie}" + os.linesep + str(output))
        return output, errs
    except subprocess.TimeoutExpired:
        ps.kill()
        # zapisuje do logu informacje o bledzie
        f_zapisz_wynik_do_pliku(plik_z_wynikiem, f"{polecenie}" + os.linesep + "error: TimeoutExpired")
        return "", "TimeoutExpired"
    except Exception as error:
        f_zapisz_wynik_do_pliku(plik_z_wynikiem, f"{polecenie}" + os.linesep + str(error))
        return "", error 

def f_zapisz_wynik_do_pliku(path, wpis):
    wynik_plik = plik_z_wynikiem
    with open(wynik_plik, '+a') as f:
        f.write(wpis)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Odpytanie shodan.io', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--ipfile', '-ipf', action='store',help='podaj sciezke do pliku')
    parser.add_argument('--results', '-r', action='store',help='podaj sciezke gdzie zapisac wynik, w przypadku nie podanie wynik zostanie zapisany w pliku z danymi z dodatkiem .wynik')
    
    args = parser.parse_args()
    path_mass_query = ""
    linii_w_pliku = 0

    plik_z_danymi = ""
    plik_z_wynikiem = ""

    if(args.ipfile):
        plik_z_danymi = args.ipfile
    else:
        sys.exit(1)

    if(args.results):
        plik_z_wynikiem = args.results
    else:
        plik_z_wynikiem = plik_z_danymi + ".wynik"

    f_odczyt_pliku(plik_z_danymi)
