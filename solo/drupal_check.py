import argparse
import ssl
import urllib.request
from bs4 import BeautifulSoup
import json


def f_check_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    resp = urllib.request.urlopen(url, context=ctx,timeout=10)
    parser = 'html.parser'
    soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))
    
    for line in soup.find_all('meta'):
            if("Drupal" in str(line).strip()):
                ver_from = str(line).find('"')
                ver_to = str(line)[ver_from+1:].find('"')
                wersja = str(line)[ver_from+1:ver_from+1+ver_to]
                
                wersja_nr = wersja.strip().split(" ")
                f_check_eol_drupal_online(str(wersja_nr[1]))
                
                print(wersja_nr)
    

def f_check_eol_drupal_online(wersja):
    url = "https://endoflife.date/api/drupal.json"
    wynik = ''

    resp = urllib.request.urlopen(url)
    data = resp.read()
     
    j = json.loads(data.decode("utf-8"))

    #data = json.load(f)
    for i in j:
        if(wersja in i['cycle']):
            print(i)


#####################################################################################################################
if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='Drupal CMS check',
        formatter_class=argparse.RawTextHelpFormatter
        )
    

    parser.add_argument('-u', '--url', action='store', dest='url_input', type=str, 
                        help='Adres strony do sprawdzenia')
    args = parser.parse_args()

    f_check_url(args.url_input)