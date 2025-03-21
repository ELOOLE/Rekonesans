from lib2to3.pgen2.token import NEWLINE
import os
import argparse
import sys

from rekonesans import f_czas
from f_biblioteka import f_polecenie_uniwersalne

def f_odczyt_pliku_lina_po_linii(plik):
    uchwyt_pliku_z_danymi = open(plik, 'r')

    for linijka in uchwyt_pliku_z_danymi:
        wynik = linijka.strip()
        Twynik = wynik.split(":")
        ip = Twynik[0]
        port = Twynik[1]

        print(f"{str(f_czas())} | IP:{ip}, port:{port}")

        if(port == "80"):
            protokol = "http"
        else:
            protokol = "https"

        with open(path_plik_logu, "a") as f:
            
            f.write(f"-------------------------------------------------{os.linesep}")
            f.write(str(f_czas()) + f"| IP:{ip}, port:{port}" + os.linesep)
            f.write(f"-------------------------------------------------{os.linesep}")

            wynik = f_polecenie_uniwersalne(f"dirb {protokol}://{ip} /usr/share/wordlists/dirb/common.txt")
            if(wynik[1] != "None"):
                try:
                    sukces = str(wynik[0].decode("utf-8"))
                except Exception as e:
                    print(e)

                f.write(sukces)
            else:
                f.write(str(wynik[1]))

    return 0

if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description='Automat do dirb-a',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str,
                        help='Podaj sciezke do pliku z adresami')
    #parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()
    
    # odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_dane = '/home/user/kbw_ver1'
    else:
        path_plik_dane = args.fin

    if(os.path.isfile(path_plik_dane)):
        '''sprawdza czy plik istnieje'''
        path_plik_logu = path_plik_dane + "_dirb_automat.log"
        path_plik_json = path_plik_dane + "_dirb_automat.json"
        path_plik_html = path_plik_dane + "_dirb_automat.html"
    else:
        print("Plik z danymi nie istnieje!" + path_plik_dane)
        sys.exit(1)
            
    # wywolujemy funkcje, ktora odczyta nam plik linijka po linijce
    f_odczyt_pliku_lina_po_linii(path_plik_dane)
