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
import os
import argparse
import sys
from f_biblioteka import style, f_czas, f_zapis_log
from read_data_file import f_odczyt_pliku


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
    parser.add_argument('-b', '--behavior', action='store', dest='scan_behavior', type=str, default=False,
                        help='True = agresywny tryb skanowania, brak lub False nie agresywny tryb skanowania')
    parser.add_argument('-cmt', '--curl-max-time', action='store', dest='curl_max_time', type=int, default=7,
                        help='Value of max timeout')
    args = parser.parse_args()


    if ('file_input' not in args or not args.file_input):
        parser.print_help()
        sys.exit(1)
    else:
        path_file_data = args.file_input

        # sprawdza czy plik istnieje
        if(os.path.isfile(path_file_data)):
            if ('file_output' not in args or not args.file_output):
                # wynik skanowania zostanie zapisany w lokalizacji pliku z danymi.
                print(style.YELLOW("[-fout] Nie wprowadzono docelowego miejsca zapisu przeznaczonego na wyniki. Zapis wyniku w lokalizacji pliku z danymi."), flush=True)   
                path_plik_logu = args.file_input + ".log"
            else:
                path_plik_logu = args.file_output + ".log"

            # wyswietlenie czasu rozpoczęcia skanowania
            start_script = f_czas()
            print(style.BLUE(f"Rozpoczynam: {start_script}"), flush=True) 

            # zapis do logu
            f_zapis_log('main','info',start_script,pathLogFile=path_plik_logu)

            # wywolujemy funkcje, ktora odczyta plik z danymi linijka po linijce
            f_zapis_log(
                "f_odczyt_pliku_nmap",
                "info",
                f"odczytuje plik z danymi: {path_file_data}",
                pathLogFile=path_plik_logu)

            f_odczyt_pliku(path_file_data)
        else:
            print(style.RED(f"[-fin] Plik z danymi [{path_file_data}] nie istnieje!"))
            sys.exit(1) 
