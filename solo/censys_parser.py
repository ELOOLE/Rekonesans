import argparse
import os
import re
import sys
from tkinter.messagebox import NO


def f_policz_wiersze_w_pliku(path):
    '''liczy ilosc linijek w wierszu'''
    '''zwraca: int, ilosc linijek w podanym pliku'''
    # otwieram plik
    otwarty_plik = open(path, "r")
    line_count = 0
    # czytam linijce po linijce
    for line in otwarty_plik:
        if line != "\n":
            line_count += 1

    # zamykam plik
    otwarty_plik.close()
    # zwracam wynik
    return line_count


def f_odczyt_pliku(plik):
    LINE_COUNT = f_policz_wiersze_w_pliku(plik)
    licznik = 1
    # otwieram plik            
    uchwyt_pliku_dane = open(plik, 'r')
    IP=""
    opis=""
    plik_po = f"{plik}_output"
    with open(plik_po, 'w') as file:
                file.write("---")

    r = re.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}")

    for linijka in uchwyt_pliku_dane:
        print(f"Postep: {licznik}\{LINE_COUNT}")
        licznik+=1
        linijka = linijka.strip()
        if "(" in linijka:
            wynik = linijka.split('(')
            ip = wynik[0]
            op = wynik[1]
            
            if r.match(ip) is None:
                print(f"pomijam: {ip}")
            else:
                IP = ip    
                opis = op[:-1]
        elif r.match(linijka) is not None:
            IP = linijka
        
        if "/" in linijka:    
            linijka = linijka.replace("/",",tcp,")
            linijka = f'{IP},{linijka},"{opis}"{os.linesep}'

            
            with open(plik_po, 'a+') as file:
                file.write(linijka)

    
####################################################################################################################
if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='censys parser',
        formatter_class=argparse.RawTextHelpFormatter
        )

    parser.add_argument('-fin', '--file-input', action='store', dest='file_input', type=str, 
                        help='Ścieżke do pliku z danymi. Plik źródłowy')
    args = parser.parse_args()

    if ('file_input' not in args or not args.file_input):
        parser.print_help()
        sys.exit(1)
    else:
        path_file_data = args.file_input
        f_odczyt_pliku(path_file_data)
