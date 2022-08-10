import os
import argparse
import random
import sys
import requests


def f_odczyt_pliku_lina_po_linii(plik):
    try:
        uchwyt_pliku_z_danymi = open(plik, 'r')
    except Exception as e:
        print(e)

    for linijka in uchwyt_pliku_z_danymi:
        url = linijka.strip()

        http = requests.session()
        req = http.get(url, timeout=TIME_OUT, verify=False, allow_redirects=True, headers=def_header())
        raw = req.content.decode(encoding='utf-8', errors='ignore')

        print(raw)

        rok_start=url.find('=')
        rok=url[rok_start+1:rok_start+5]

        plik_zapisu = f"/home/nano/Documents/Filatelistyka/test/{rok}.html"
        print(f"Zapisuje do pliku: {plik_zapisu}")

        zawartosc = wynik[0].decode("latin-1")

        try:
            
            with open(plik_zapisu, "w", encoding='utf-8') as f:
                f.write(zawartosc)
            #print(wynik[0])

            print(f"Zapisano plik: {plik_zapisu}")
        except Exception as e:
            print(e)

        #f.write(adres)

def random_ua():
    USER_AGENT_PARTS = {
        'os': {
            'linux': {
                'name': ['Linux x86_64', 'Linux i386'],
                'ext': ['X11']
            },
            'windows': {
                'name': ['Windows NT 10.0', 'Windows NT 6.1', 'Windows NT 6.3', 'Windows NT 5.1', 'Windows NT.6.2'],
                'ext': ['WOW64', 'Win64; x64']
            },
            'mac': {
                'name': ['Macintosh'],
                'ext': ['Intel Mac OS X %d_%d_%d' % (random.randint(10, 11), random.randint(0, 9), random.randint(0, 5))
                        for
                        i in range(1, 10)]
            },
        },
        'platform': {
            'webkit': {
                'name': ['AppleWebKit/%d.%d' % (random.randint(535, 537), random.randint(1, 36)) for i in range(1, 30)],
                'details': ['KHTML, like Gecko'],
                'extensions': ['Chrome/%d.0.%d.%d Safari/%d.%d' % (
                    random.randint(6, 32), random.randint(100, 2000), random.randint(0, 100), random.randint(535, 537),
                    random.randint(1, 36)) for i in range(1, 30)] + ['Version/%d.%d.%d Safari/%d.%d' % (
                    random.randint(4, 6), random.randint(0, 1), random.randint(0, 9), random.randint(535, 537),
                    random.randint(1, 36)) for i in range(1, 10)]
            },
            'iexplorer': {
                'browser_info': {
                    'name': ['MSIE 6.0', 'MSIE 6.1', 'MSIE 7.0', 'MSIE 7.0b', 'MSIE 8.0', 'MSIE 9.0', 'MSIE 10.0'],
                    'ext_pre': ['compatible', 'Windows; U'],
                    'ext_post': ['Trident/%d.0' % i for i in range(4, 6)] + [
                        '.NET CLR %d.%d.%d' % (random.randint(1, 3), random.randint(0, 5), random.randint(1000, 30000))
                        for
                        i in range(1, 10)]
                }
            },
            'gecko': {
                'name': ['Gecko/%d%02d%02d Firefox/%d.0' % (
                    random.randint(2001, 2010), random.randint(1, 31), random.randint(1, 12), random.randint(10, 25))
                         for i
                         in
                         range(1, 30)],
                'details': [],
                'extensions': []
            }
        }
    }
    # Mozilla/[version] ([system and browser information]) [platform] ([platform details]) [extensions]
    ## Mozilla Version
    mozilla_version = "Mozilla/5.0"  # hardcoded for now, almost every browser is on this version except IE6
    ## System And Browser Information
    # Choose random OS
    os = USER_AGENT_PARTS.get('os')[random.choice(list(USER_AGENT_PARTS.get('os').keys()))]
    os_name = random.choice(os.get('name'))
    sysinfo = os_name
    # Choose random platform
    platform = USER_AGENT_PARTS.get('platform')[random.choice(list(USER_AGENT_PARTS.get('platform').keys()))]
    # Get Browser Information if available
    if 'browser_info' in platform and platform.get('browser_info'):
        browser = platform.get('browser_info')
        browser_string = random.choice(browser.get('name'))
        if 'ext_pre' in browser:
            browser_string = "%s; %s" % (random.choice(browser.get('ext_pre')), browser_string)
        sysinfo = "%s; %s" % (browser_string, sysinfo)
        if 'ext_post' in browser:
            sysinfo = "%s; %s" % (sysinfo, random.choice(browser.get('ext_post')))
    if 'ext' in os and os.get('ext'):
        sysinfo = "%s; %s" % (sysinfo, random.choice(os.get('ext')))
    ua_string = "%s (%s)" % (mozilla_version, sysinfo)
    if 'name' in platform and platform.get('name'):
        ua_string = "%s %s" % (ua_string, random.choice(platform.get('name')))
    if 'details' in platform and platform.get('details'):
        ua_string = "%s (%s)" % (
            ua_string,
            random.choice(platform.get('details')) if len(platform.get('details')) > 1 else platform.get(
                'details').pop())
    if 'extensions' in platform and platform.get('extensions'):
        ua_string = "%s %s" % (ua_string, random.choice(platform.get('extensions')))
    return ua_string

def def_header():
    DEFAULT_HEADER = {
        'user-agent': random_ua(),
        'referer': 'https://www.google.com/',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
    }

    return DEFAULT_HEADER

#################################################
if __name__ == '__main__':
    '''MAIN'''    
    parser = argparse.ArgumentParser(
        description='Automat do curl-a',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-fin', '--file-input', type=str, action='store', dest='file_input'
    , help='Podaj sciezke do pliku z adresami')
    args = parser.parse_args()
    
    TIME_OUT = 15

    # odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_dane = '/home/user/kbw_ver1'
    else:
        path_plik_dane = args.fin

    if(os.path.isfile(path_plik_dane)):
        '''sprawdza czy plik istnieje'''
        path_plik_logu = path_plik_dane + "_curl_automat.log"
        path_plik_json = path_plik_dane + "_curl_automat.json"
        path_plik_html = path_plik_dane + "_curl_automat.html"
    else:
        print("Plik z danymi nie istnieje!" + path_plik_dane)
        sys.exit(1)
            
    # wywolujemy funkcje, ktora odczyta nam plik linijka po linijce
    f_odczyt_pliku_lina_po_linii(path_plik_dane)
