import argparse
import csv
import json
import os
import re
from tkinter import E
import pandas as pd


def f_odczyt_pliku(filePathData,filePathDataCSV):
    # otwieram ponownie
    h_filePathData = open(filePathData, 'r')

    data = {}
    data['skan'] = []
    array_ip = []
    array_ip_tcp = []
    array_ip_udp = []

    for linijka in h_filePathData:
        linijka = linijka.strip()
        linijka = linijka.replace('"','')
        wynik = linijka.split(',')

        ip = wynik[0]
        port = wynik[1]
        protokol = wynik[2]

        r = re.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}")
        if r.match(ip) is None:
            print(f"To nie IP:{ip}")
        else:
            # zapis do pliku *.json
            tmp_dict = {ip: {
                'port': port,
                'protokol': protokol
            }}

            print(f">> ip: {ip}, port: {port}, protokol: {protokol}\n")

            try:
                index_szukana = array_ip.index(ip)
                if(str.lower(protokol) == 'tcp'):
                    port_tcp = array_ip_tcp[index_szukana]

                    if len(port_tcp) == 0:
                        array_ip_tcp[index_szukana] = port
                    else:
                        array_ip_tcp[index_szukana] = port_tcp + ',' + port
                    
                    #print('arr tcp: ' + str(array_ip_tcp))
                else:
                    port_udp = array_ip_udp[index_szukana]

                    if len(port_udp) == 0:
                        array_ip_udp[index_szukana] = port
                    else:
                        array_ip_udp[index_szukana] = port_udp + ',' + port
                    
                    #print('arr udp: '+str(array_ip_udp))
                
            except Exception as e:
                #print('wyjatek'+str(e))
                array_ip.append(ip)
                index_szukana = array_ip.index(ip)

                print('index_szukana'+str(index_szukana))

                if(str.lower(protokol) == 'tcp'):              
                    array_ip_tcp.append(port)
                    array_ip_udp.append('')
                    #print('tcp: '+port)
                else:
                    array_ip_tcp.append('')
                    array_ip_udp.append(port)
                    #print('udp: '+port)

            #print(str(array_ip))

            #input("")
            data['skan'].append(tmp_dict)

    plik_csv_dane = ''

    for element in array_ip:
        index_szukana = array_ip.index(element)
        plik_csv_dane = plik_csv_dane + element+';' + array_ip_tcp[index_szukana]+';' + array_ip_udp[index_szukana]+';\n'
        
    #print(plik_csv_dane) 

    try:
        with(open(filePathDataCSV, 'w')) as f:
            f.write(plik_csv_dane)
        print(f"Zapisano do pliku: {filePathDataCSV}")
    except Exception as e:
        print(e)
    
    wynik = f_zapisz_dane_jako_json(data, path_plik_json)

def f_zapisz_dane_jako_json(data, dstfile):
    wynik = ""
    try:
        with open(dstfile, 'a+') as outfile:
            json.dump(data, outfile)
        wynik = "sukces"
    except Exception as e:
        wynik = str(e)

    return wynik


if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description='Parser msfconsole export services -u wersja 0.1',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str,
                        help='Podaj sciezke do pliku z adresami')

    args = parser.parse_args()

    # odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_dane = '/home/user/MKiS_wan_bb.txt'
    else:
        path_plik_dane = args.fin

    if(os.path.isfile(path_plik_dane)):
        path_plik_json = path_plik_dane + ".json"
        path_plik_csv = path_plik_dane + ".csv"

        # wywolujemy funkcje, ktora odczyta nam plik linijka po linijce
        f_odczyt_pliku(path_plik_dane, path_plik_csv)
    else:
        print("Plik z danymi nie istnieje!" + path_plik_dane)
