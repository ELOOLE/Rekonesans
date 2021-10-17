import subprocess
import argparse
import datetime
import tldextract
import pyfiglet

baner = pyfiglet.figlet_format("WebTOOL")
print(baner)

def dane (URL,OUT):
    czas = datetime.datetime.now()
    ext = tldextract.extract(URL)
    cleanurl = ext.fqdn
    print("Program do testowania stron WWW")
    print("Skanowanie - proszę czekać ...")
    welcome = subprocess.check_call(f'echo Skanowanie roczpoczęte {czas} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    i = print("1/8 - Skanowanie programem NIKTO")
    nikto = subprocess.check_call(f'nikto -host {cleanurl} -ask no >> {OUT}', shell=True, stdout=subprocess.PIPE)
    i = print("2/8 - Skanowanie programem DIRB")
    dirb = subprocess.check_call(f'dirb {URL} -f -r >> {OUT}', shell=True, stdout=subprocess.PIPE)
    i = print("3/8 - Skanowanie programem CLUSTERD")
    clusterd = subprocess.check_call(f'clusterd -i {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    i = print("4/8 - Skanowanie programem JOOMSCAN")
    joomscan = subprocess.check_call(f'joomscan -u {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    i = print("5/8 - Skanowanie programem WAPITI")
    wapiti = subprocess.check_call(f'wapiti -u {URL} -v 1 >> {OUT}', shell=True, stdout=subprocess.PIPE)
    i = print("6/8 - Skanowanie programem WHATWEB")
    whatweb = subprocess.check_call(f'whatweb {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    i = print("7/8 - Skanowanie programem NMAP")
    nmap = subprocess.check_call(f'nmap --script http-enum {cleanurl} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    nmap = subprocess.check_call(f'nmap --script http-title -sV -p 80 {cleanurl} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    nmap = subprocess.check_call(f'nmap -n -p80 --script http-config-backup {cleanurl} >> {OUT}', shell=True, stdout=subprocess.PIPE)
    nmap = subprocess.check_output(f'nmap -sV -p80 --script vuln {cleanurl} >> {OUT}', shell=True, stderr=subprocess.STDOUT)
    i = print("8/8 - Skanowanie programem WPSCAN")
    wpscan = subprocess.Popen(f'wpscan --url {URL} --random-user-agent >> {OUT}', shell=True, stdout=subprocess.PIPE)
    print(f'Plik z raportem znajduje się w katalogu {OUT}')
    exit()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--u', '--url', type=str,
                        help='Wprowadz pełny adres URL z http lub https')
    parser.add_argument('--o', '--output', type=str, default='/home/webreport.txt',
                        help='Wprowadz sciezke do pliku wynikowego, default="/home/webreport.txt"')
    args = parser.parse_args()
    URL = args.u
    OUT = args.o
    dane(URL,OUT)
