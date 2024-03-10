###############################################################################
# rekonesans v0.2
# Written by MM
# Copyright 2021
#---
# nmap -sV -A -O -p- XcelX -oA PlikWynikowy
#---
# services -u -O 1 -c  port,proto,name,info -o /home/user/targets_ports - sort by host
# services -u -O 2 -c  port,proto,name,info -o /home/user/targets_ports - sort by port
###############################################################################
from multiprocessing.pool import ThreadPool
import os
import argparse
from pickle import FALSE
import sys
from tkinter.ttk import Style
from xmlrpc.client import boolean
import f_biblioteka, f_json
import read_data_file

#####################################################################################################################
if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='Rekonesans MM wersja 0.1b',
        formatter_class=argparse.RawTextHelpFormatter
        )

    parser.add_argument('-fin', '--file-input', action='store', dest='file_input', type=str, 
                        help='Ścieżke do pliku z danymi. Plik źródłowy')
    parser.add_argument('-fout', '--file-output', action='store', dest='file_output', type=str, 
                        help='Ścieżke do zapisu pliku z wynikami skanowania')
    parser.add_argument('-b', '--behavior', action='store', dest='scan_behavior', type=boolean, 
                        help='True = agresywny tryb skanowania, brak lub False nie agresywny tryb skanowania')
    parser.add_argument('-cmt', '--curl-max-time', action='store', dest='curl_max_time', type=int, 
                        help='Value of max timeout')
    parser.add_argument('-st', '--scan-tag', action='store', dest='scan_tag', type=str, 
                        help='frendly project (scan) name')
    parser.add_argument('-fl', '--from-line', action='store', dest='from_line', type=str, 
                        help='From line')
    args = parser.parse_args()


    if ('scan_behavior' not in args or not args.scan_behavior):
        AGGRESIVE=False
        print(f_biblioteka.style.YELLOW("Aggresive mode scan: default False, use -b True to change that"))
    elif(args.scan_behavior==True):
        AGGRESIVE=True

    if ('curl_max_time' not in args or not args.curl_max_time):
        CURL_MAX_TIME = 7
        print(f_biblioteka.style.YELLOW("curl --max-time default set to 7, use -cmt int to change that"))
    elif(args.curl_max_time != 7):
        CURL_MAX_TIME=args.curl_max_time
    
    if ('scan_tag' not in args or not args.scan_tag):
        scan_tag = 'projekt1'
        print(f_biblioteka.style.YELLOW("scan_tag default set to 'projekt1', use -st str to change that"))
    elif(args.curl_max_time != 7):
        TAG_OF_THE_SKAN=args.scan_tag

    if ('file_input' not in args or not args.file_input):
        parser.print_help()
        sys.exit(1)
    else:
        path_file_data = args.file_input

        # sprawdza czy plik istnieje
        if(os.path.isfile(path_file_data)):
            if ('file_output' not in args or not args.file_output):
                # wynik skanowania zostanie zapisany w lokalizacji pliku z danymi.
                print(f_biblioteka.style.YELLOW("[-fout] Nie wprowadzono docelowego miejsca zapisu przeznaczonego na wyniki. Zapis wyniku w lokalizacji pliku z danymi."), flush=True)   
                path_plik_logu = args.file_input + ".log"
                path_plik_json = args.file_input + ".json"
                path_plik_html = args.file_input + ".html"
            else:
                path_plik_logu = args.file_output + ".log"
                path_plik_json = args.file_output + ".json"
                path_plik_html = args.file_output + ".html"
                FILE_OUTPUT = args.file_output

            # wyswietlenie czasu rozpoczęcia skanowania
            start_script = f_biblioteka.f_czas()
            print(f_biblioteka.style.BLUE(f"Rozpoczynam: {start_script}"), flush=True) 

            # zapis do logu
            f_biblioteka.f_zapis_log('main','info',start_script,pathLogFile=path_plik_logu)

            # wywolujemy funkcje, ktora odczyta plik z danymi linijka po linijce
            f_biblioteka.f_zapis_log(
                "f_odczyt_pliku_nmap",
                "info",
                f"odczytuje plik z danymi: {path_file_data}",
                pathLogFile=path_plik_logu)

            read_data_file.f_odczyt_pliku_nmap(path_file_data)
        else:
            print(f_biblioteka.style.RED(f"[-fin] Plik z danymi [{path_file_data}] nie istnieje!"))
            sys.exit(1) 
