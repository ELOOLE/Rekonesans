import subprocess
import argparse
import datetime
import tldextract
import progressbar

def dane (URL,OUT):
    czas = datetime.datetime.now()
    ext = tldextract.extract(URL)
    cleanurl = ext.domain + '.' + ext.suffix
    # bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
    # for l in range(20):
    for l in progressbar.progressbar(range(2), redirect_stdout=True):
        print("Program do testowania stron WWW")
        # bar.update(l)
        print("Skanowanie - proszę czekać ...")
        # bar.update(l)
        welcome = subprocess.check_call(f'echo Skanowanie roczpoczęte {czas} >> {OUT}', shell=True, stdout=subprocess.PIPE)
        i = print("1/8 - Skanowanie programem NIKTO",l)
        # bar.update(l)
        nikto = subprocess.check_call(f'nikto -host {cleanurl} -ask no >> {OUT}', shell=True, stdout=subprocess.PIPE)
        # bar.update(l)
        i = print("2/8 - Skanowanie programem DIRB",l)
        # bar.update(l)
        dirb = subprocess.check_call(f'dirb {URL} -f -r -o {OUT}', shell=True, stdout=subprocess.PIPE)
        # bar.update(l)
        i = print("3/8 - Skanowanie programem CLUSTERD")
        # bar.update(l)
        clusterd = subprocess.check_call(f'clusterd -i {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
        # bar.update(l)
        i = print("4/8 - Skanowanie programem JOOMSCAN")
        # bar.update(l)
        joomscan = subprocess.check_call(f'joomscan -u {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
        # bar.update(l)
        i = print("5/8 - Skanowanie programem WAPITI")
        wapiti = subprocess.check_call(f'wapiti -u {URL} -v 1 >> {OUT}', shell=True, stdout=subprocess.PIPE)
        # bar.update(l)
        i = print("6/8 - Skanowanie programem WHATWEB")
        # bar.update(l)
        whatweb = subprocess.check_call(f'whatweb {URL} >> {OUT}', shell=True, stdout=subprocess.PIPE)
        # bar.update(l)
        i = print("7/8 - Skanowanie programem NMAP")
        # bar.update(l)
        nmap = subprocess.check_call(f'nmap --script http-enum {cleanurl} >> {OUT}', shell=True, stdout=subprocess.PIPE)
        nmap = subprocess.check_call(f'nmap --script http-title -sV -p 80 {cleanurl} >> {OUT}', shell=True, stdout=subprocess.PIPE)
        nmap = subprocess.check_call(f'nmap -n -p80 --script http-config-backup {cleanurl} >> {OUT}', shell=True, stdout=subprocess.PIPE)
        nmap = subprocess.check_output(f'nmap -sV -p80 --script vuln {cleanurl} >> {OUT}', shell=True, stderr=subprocess.STDOUT)
        # bar.update(l)
        i = print("8/8 - Skanowanie programem WPSCAN")
        # bar.update(l)
        wpscan = subprocess.Popen(f'wpscan --url {URL} --random-user-agent >> {OUT}', shell=True, stdout=subprocess.PIPE)
        print(f'Plik z raportem znajduje się w katalogu {OUT}')
        # bar.update(l)
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
