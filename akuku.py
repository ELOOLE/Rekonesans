  
import os
from re import sub
import re
import time
import subprocess, signal
import argparse
import datetime
import pyfiglet

import json
from json2html import *

# dane do zrzutu danych
data = {}

#banner aplikacji
baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def f_odczyt_pliku_nmap(plik):
    czas = datetime.datetime.now()
    print(f"{czas} | odczytuje plik z danymi: {plik}")
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

    data['host'] = []
    
    # czytamy linijka po linijce 
    for linijka in otwarty_plik_nmap:
        #czas otwarcia kolejnej linijki
        czas = datetime.datetime.now()

        #print(f"linijka: {linijka}")

        # rozpoczynamy parsowanie pliku
        # services -u -c port,proto,name,info - o /home/user/rand1234
        wynik = linijka.split(',')
        ip = wynik[0].replace("\"", "").rstrip("\n")
        port = wynik[1].replace("\"", "").rstrip("\n")
        protokol = wynik[2].replace("\"", "").rstrip("\n")
        usluga = wynik[3].replace("\"", "").rstrip("\n")
        opis_nmap = wynik[4].replace("\"", "").rstrip("\n")

        print(f"({i}/{line_count}) | {czas} | IP: {ip} proto:{protokol} port:{port} usluga: {usluga}")
        i+=1

        r = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if r.match(ip) is None:
            print(f"{czas} | Wpis nie zawiera poprawnego adresu IP [{ip}]")
        else:
            # pierwsza funkcja socat na określenie hosta
            output_socat = f_socat(ip,port,protokol)

            # curl - odpytuje host i daje info dla wykonania screen shota 
            output_curl = f_curl(ip,port,protokol)

            # screen shot w przypadku kiedy curl zwroci 200, 302, 404
            output_screen_shot_web = "---"
            if(" 200 " in str(output_curl) or " 302 " in str(output_curl) or " 404 " in str(output_curl)):
                output_screen_shot_web = f_screen_shot_web(ip,port,protokol)

            # zapis do pliku *.json
            data['host'].append({'ip':f'{ip}','port':f'{port}','protokol':f'{protokol}','usluga':f'{usluga}','opis':f'{opis_nmap}','socat':f'{output_socat}','curl':f'{output_curl}','screen_shot':f'{output_screen_shot_web}'})
        
    with open('/home/nano/data.json', 'w') as outfile:
        json.dump(data, outfile)
    
    #'/home/nano/data.txt'
    #infoFromJson = json.loads(data)
    build_direction = "LEFT_TO_RIGHT"
    table_attributes = {"style": "width:100%"}
    #print(json2html.convert(infoFromJson, build_direction=build_direction, table_attributes=table_attributes))
    #print(json2html.convert(json = data, build_direction=build_direction, table_attributes=table_attributes))

    raport_html = open('/home/nano/data.hml', 'w')
    raport_html = json2html.convert(json = data, build_direction=build_direction, table_attributes=table_attributes)


    
    otwarty_plik_nmap.close()

def f_socat(ip,port,protokol):
    czas = datetime.datetime.now()
    cmd = ""
    if(protokol == "tcp"):
        cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 TCP:{ip}:{port},connect-timeout=2 - "
    else:
        cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 UDP:{ip}:{port},connect-timeout=2 - "
    
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]

    return output

def f_curl(ip,port,protokol):
    czas = datetime.datetime.now()

def f_screen_shot_web (ip,port,protokol):
    czas = datetime.datetime.now()

def f_get_links_from_web(ip,port,protokol):
    czas = datetime.datetime.now()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Rekonesans MM wersja 0.1', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str, help='Podaj sciezke do pliku z adresami')
    parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # odczytujemy plik z metasploit
    # services -u -c proto,port,name -o /home/user/Pobrane/dane.txt
    # services -u -c port,proto,name,info - o /home/user/rand1234
    # odczyt pliku

    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_nmap_msfconsole = '/home/nano/test1'
    else:
        path_plik_nmap_msfconsole = args.fin
    
    # wywołujemy funkcję, która odczyta nam plik linijka po linijce
    f_odczyt_pliku_nmap(path_plik_nmap_msfconsole)