  
import os
from re import sub
import re
import time
import subprocess, signal
import argparse
import datetime
import pyfiglet

#banner aplikacji
baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def odczyt_pliku_nmap(plik):
    otwarty_plik_nmap = open(plik, 'r')

    # licze ile jest lini w pliku z danymi
    line_count = 0
    for line in otwarty_plik_nmap:
        if line != "\n":
            line_count += 1
    otwarty_plik_nmap.close()
    print(f"Ilosc zadan do wykonania: {line_count} \n")

    # otwieram ponownie
    otwarty_plik_nmap = open(plik, 'r')
    i = 1

    # czytamy linijka po linijce 
    for linijka in plik.readlines():
        #czas otwarcia kolejnej linijki
        czas = datetime.datetime.now()

        # rozpoczynamy parsowanie pliku
        wynik = linijka.split(',')
        ip = wynik[0].replace("\"", "").rstrip("\n")
        protokol = wynik[1].replace("\"", "").rstrip("\n")
        port = wynik[2].replace("\"", "").rstrip("\n")
        usluga = wynik[3].replace("\"", "").rstrip("\n")

        print(f"{czas} | IP: {ip} proto:{protokol} port:{port} usluga: {usluga} ({i}/{line_count})")
        i+=1
    
    otwarty_plik_nmap.close()

def socat(ip,port,protokol):
    czas = datetime.datetime.now()
    cmd = ""
    if(protokol == "tcp"):
        cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 TCP:{ip}:{port},connect-timeout=2 - "
    else:
        cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 UDP:{ip}:{port},connect-timeout=2 - "

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Rekonesans MM wersja 0.1', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str, help='Podaj sciezke do pliku z adresami')
    parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # odczytujemy plik z metasploit
    # services -u -c proto,port,name -o /home/user/Pobrane/dane.txt
    # odczyt pliku
    path_plik_nmap_msfconsole = args.fin

    # wywołujemy funkcję, która odczyta nam plik linijka po linijce
    odczyt_pliku_nmap(path_plik_nmap_msfconsole)