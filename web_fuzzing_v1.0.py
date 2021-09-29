import subprocess
import argparse
import datetime
import tldextract
import os
# import progressbar

def dane (URL,OUT,SECLISTS):
    czas = datetime.datetime.now()
    ext = tldextract.extract(URL)
    wordlistsxss = [xss for xss in os.listdir(f'{SECLISTS}/Fuzzing/XSS') if xss.endswith('.txt')]
    wordlistsdb = [db for db in os.listdir(f'{SECLISTS}/Fuzzing/Databases') if db.endswith('.txt')]
    wordlistscm = [cm for cm in os.listdir(f'{SECLISTS}/Fuzzing') if cm.endswith('.txt')]
    cleanurl = ext.domain + '.' + ext.suffix
    print("Program do testowania WWW - Fuzzing")
    print("Fuzzing - proszę czekać ...")
    welcome = subprocess.check_call(f'echo Fuzzing roczpoczęty {czas} >> {OUT}', shell=True, stdout=subprocess.PIPE)

    i = print("1/3 - Fuzzing COMMONLISTS")
    for cm in wordlistscm:
        ffufcm = subprocess.check_call(f'ffuf -w {SECLISTS}/Fuzzing/{cm} -u {URL}FUZZ -x GET>> {OUT}',
                                       shell=True, stdout=subprocess.PIPE)

    i = print("2/3 - Fuzzing XXS")
    for xss in wordlistsxss:
        ffufxxs = subprocess.check_call(f'ffuf -w {SECLISTS}/Fuzzing/XSS/{xss} -u {URL}FUZZ -x GET>> {OUT}', shell=True, stdout=subprocess.PIPE)
        ffufxxs2 = subprocess.check_call(f'ffuf -w {SECLISTS}/Fuzzing/Polyglots/{xss} -u {URL}FUZZ -x GET>> {OUT}', shell=True,
                                    stdout=subprocess.PIPE)

    i = print("3/3 - Fuzzing DATABASES")
    for db in wordlistsdb:
        ffufdb = subprocess.check_call(f'ffuf -w {SECLISTS}/Fuzzing/Databases/{db} -u {URL}FUZZ -x GET>> {OUT}',
                                            shell=True, stdout=subprocess.PIPE)

    print(f'Plik z raportem znajduje się w katalogu {OUT}')

    exit()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--u', '--url', type=str,
                        help='Wprowadz pełny adres URL z http lub https')
    parser.add_argument('--o', '--output', type=str, default='/home/webreport.txt',
                        help='Wprowadz sciezke do pliku wynikowego, default="/home/webreport.txt"')
    parser.add_argument('--s', '--seclists', type=str, default='/home/SecLists',
                        help='Wprowadz sciezke do pliku zawierającego słowniki SecList, default="/home/SecLists"')
    args = parser.parse_args()
    URL = args.u
    OUT = args.o
    SECLISTS = args.s
    dane(URL,OUT,SECLISTS)
