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
    path = OUT + cleanurl
    print("Program do testowania stron WWW")
    print("Skanowanie - proszę czekać ...")
    box_raport = subprocess.check_call(f'mkdir {path}', shell=True, stdout=subprocess.PIPE)
    welcome = subprocess.check_call(f'echo Skanowanie roczpoczęte {czas} >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    i = print("1/8 - Skanowanie programem NIKTO")
    nikto = subprocess.check_call(f'nikto -host {cleanurl} -ask no >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    i = print("2/8 - Skanowanie programem DIRB")
    dirb = subprocess.check_call(f'dirb {URL}/ -f -r >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    i = print("3/8 - Skanowanie programem SKIPFISH")
    skipfish = subprocess.check_call(f'skipfish -u -o {path}/skipfish_report {URL}', shell=True, stdout=subprocess.PIPE)
    i = print("4/8 - Skanowanie programem JOOMSCAN")
    joomscan = subprocess.check_call(f'joomscan -u {URL} >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    i = print("5/8 - Skanowanie programem WAPITI")
    wapiti = subprocess.check_call(f'wapiti -u {URL} -v 1 --max-attack-time 20 -o {path}/wapiti_report', shell=True, stdout=subprocess.PIPE)
    i = print("6/8 - Skanowanie programem WHATWEB")
    whatweb = subprocess.check_call(f'whatweb {URL} >> {OUT}{cleanurl}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    i = print("7/8 - Skanowanie programem NMAP")
    nmap = subprocess.check_call(f'nmap --script http-enum {cleanurl} >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    nmap = subprocess.check_call(f'nmap --script http-title -sV -p80,443 {cleanurl} >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    nmap = subprocess.check_call(f'nmap -n -p80,443 --script http-config-backup {cleanurl} >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    nmap = subprocess.check_output(f'nmap -sV -p80,443 --script vuln {cleanurl} >> {path}/webtool_scan.txt', shell=True, stderr=subprocess.STDOUT)
    i = print("8/8 - Skanowanie programem WPSCAN")
    wpscan = subprocess.check_call(f'wpscan --update', shell=True, stdout=subprocess.PIPE)
    wpscan = subprocess.Popen(f'wpscan --url {URL} --random-user-agent >> {path}/webtool_scan.txt', shell=True, stdout=subprocess.PIPE)
    print(f'katalog {cleanurl} z raportem znajduje się w {OUT}')
    exit()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--u', '--url', type=str,
                        help='Wprowadz pełny adres URL z http lub https')
    parser.add_argument('--o', '--output', type=str, default='/home/',
                        help='Wprowadz sciezke do katalogu wynikowego, default="/home/"')
    args = parser.parse_args()
    URL = args.u
    OUT = args.o
    dane(URL,OUT)
