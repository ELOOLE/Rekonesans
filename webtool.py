import subprocess
import argparse

def dane (URL,OUT):
    print("Program do testowania stron WWW")
    print("Rozpoczynam skanowanie - proszę czekać...")
    nikto = subprocess.check_call(f'nikto -host {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    print("Ukończono 10%")
    clusterd = subprocess.check_call(f'clusterd -i {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    print("Ukończono 30%")
    joomscan = subprocess.check_call(f'joomscan -u {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    print("Ukończono 50%")
    wapiti = subprocess.check_call(f'wapiti {URL} -n 10 -v 1 >> {OUT}', shell=True, stdout=subprocess.PIPE)
    print("Ukończono 70%")
    whatweb = subprocess.check_call(f'whatweb {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    print("Ukończono 90%")
    wpscan = subprocess.check_call(f'wpscan --url {URL} --random-agent --follow-redirection >> {OUT}', shell=True, stdout=subprocess.PIPE)

    print ("Skanowanie zakończyło się, sprawdź raport w katalogu /home/webreport.txt")
    exit()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--u', '--url', type=str,
                        help='Wprowadz adres URL')
    parser.add_argument('--o', '--output', type=str, default='/home/webreport.txt',
                        help='Wprowadz sciezke do pliku wynikowego, default="/home/webreport.txt"')
    args = parser.parse_args()
    URL = args.u
    OUT = args.o
    dane(URL, OUT)
