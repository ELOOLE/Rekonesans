import os
import random
import subprocess
import datetime
import ssl
import urllib.request
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

from urllib.parse import urlparse
from PIL import Image, ImageFont, ImageDraw

from impacket.dcerpc.v5 import transport
from impacket.dcerpc.v5.ndr import NULL
from impacket.dcerpc.v5.rpcrt import RPC_C_AUTHN_LEVEL_NONE
from impacket.dcerpc.v5.dcomrt import IObjectExporter

from rekonesans1a import style

def f_polecenie_uniwersalne(cmd):
    '''SOCAT
    INPUT:
        cmd - command
    OUTPUT:
        wynik polecenia
    '''     
    ps = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    try:
        output, errs = ps.communicate(timeout=20)

        return output, errs
    except subprocess.TimeoutExpired:
        ps.kill()

        return "", "TimeoutExpired"
    except Exception as error:
        return "", str(error)


def f_count_str_in_file(path, szukana):
    '''liczy ilosc powtorzen ciagu znakow w tekscie'''
    # otwieram plik
    otwarty_plik = open(path, "r")
    data = otwarty_plik.read()

    wystapien = data.count(szukana)

    otwarty_plik.close()
    # zwracam wynik
    return wystapien


def f_trim_output(output):
    output = str(output)
    if(output == "b''"):
        output = ""

    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]
    
    return output


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


def f_dirb(adres):
    wynik = f_polecenie_uniwersalne(f"dirb {adres} /usr/share/wordlists/dirb/common.txt")
    
    if(wynik[1] != "None"):
        try:
            sukces = str(wynik[0].decode("utf-8"))
        except Exception as e:
            sukces = str(wynik[0])
            
    return sukces        


def f_get_links_from_web(adres):
    '''pobiera linki ze strony'''
    spis_linkow = ""
    spis_linkow_html = ""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        addrHTTP = adres
        parser = 'html.parser'

        resp = urllib.request.urlopen(addrHTTP, context=ctx,timeout=10)
        soup = BeautifulSoup(
            resp, parser, from_encoding=resp.info().get_param('charset'))

        for link in soup.find_all('a', href=True):
            spis_linkow += link['href'] + "\n"
            spis_linkow_html += link['href'] + "<br />"

    except Exception as e:
        spis_linkow = "error"
        spis_linkow_html = "error"

    return spis_linkow_html


def f_screen_shot_web(wwwadres, pathZapisu):
    '''SCREEN SHOT of WEB PAGE '''
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.headless = True
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)

        lista_adres = urlparse(wwwadres)

        # http / https
        protokol = lista_adres.scheme
        # netloc - network location
        netloc = lista_adres.netloc
        netloc = netloc.split(":")
        ip = netloc[0]
        port = netloc[1]
        # path
        #path = lista_adres.path
        if(len(netloc) == 1):
            if(protokol == "http"):
                port = "80"
            elif(protokol == "https"):
                port = "443"
        else:
            port = netloc[1]

        #URL = f"{protokol}://{ip}:{port}"
        URL = wwwadres
        ####f_zapis_log("f_screen_shot_web", "info", URL)

        driver.get(URL)
        def S(X): return driver.execute_script(
            'return document.body.parentNode.scroll' + X)
        # driver.set_window_size(1200,S('Height'))

        driver.set_window_size(S('Width'), S('Height'))
        # driver.set_window_size(1200,1200)

        # nazwa pliku *.png
        nazwa_pliku = f"{pathZapisu}_{ip}_{port}_{protokol}.png"
        ####f_zapis_log(
        ####    "f_screen_shot_web",
        ####    "info",
        ####    f"nazwa pliku screen shot-a {nazwa_pliku}")

        # tresc znaku wodnego nanoszonego na *.png
        znak_wodny = f"{f_czas()} | Protokol: [{protokol}], adres ip: [{ip}], port: [{port}]"
        ####f_zapis_log("f_screen_shot_web", "info", f"znak wodny {znak_wodny}")

        # driver.find_element_by_tag_name('body').screenshot(nazwa_pliku)
        driver.save_screenshot(nazwa_pliku)
        driver.quit()

        # nanosimy znak wodny na img
        podpisz_screena = Image.open(nazwa_pliku)
        title_font = ImageFont.truetype(
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
        title_text = znak_wodny
        image_editable = ImageDraw.Draw(podpisz_screena)
        wysokosc_img = podpisz_screena.height - 29
        szerokosc_img = podpisz_screena.width
        image_editable.rectangle(
            (0,
             wysokosc_img + 6,
             szerokosc_img - 1,
             wysokosc_img + 21),
            outline='red',
            fill='blue')
        image_editable.text((15, wysokosc_img + 5),
                            str(title_text), (165, 230, 211), font=title_font)
        podpisz_screena.save(nazwa_pliku)
        ####f_zapis_log(
        ####    "f_screen_shot_web",
        ####    "info",
        ####    f"Naniesiono podpis na obrazek: {nazwa_pliku}")

        # convert png to jpg
        nazwa_pliku_jpg = nazwa_pliku[:-3] + "jpg"
        img_to_jpg = podpisz_screena.convert('RGB')
        img_to_jpg.save(nazwa_pliku_jpg)
        ####f_zapis_log(
        ####    "f_screen_shot_web",
        ####    "info",
        ####    f"konversja {nazwa_pliku} -> {nazwa_pliku_jpg}")

        # skasowac png
        os.remove(nazwa_pliku)
        ####f_zapis_log("f_screen_shot_web","info",f"skanowano plik {nazwa_pliku}")
        obrazek = os.path.basename(nazwa_pliku_jpg)
    except Exception as error:
        ####f_zapis_log("f_screen_shot_web", "error", error)
        obrazek = "error"

    return obrazek


def f_czas():
    '''Zwraca w wyniku aktualny czas'''
    return str(datetime.datetime.now())[:19]

# budowa komunikatu w celu zapisania do pliku w zmiennej [path_plik_logu] i wyswietlenia na konsoli
# -------------------------------
# f_czas() - zwraca aktualny czas
# typ - informacyjnie, ostrzezenie, blad
# zrodlo - kto wygenerowal ten komunikat
# dane - jakie dane zawiera wynik wykonania operacji
def f_zapis_log(zrodlo, typ, dane, pathLogFile):
    '''Zapis wyniku dzialania do pliku logu'''
    '''Sciezka pliku w zmiennej [path_plik_logu]'''

    if(os.path.isfile(pathLogFile)):
        plik_logu = open(pathLogFile, 'a+')
    else:
        plik_logu = open(pathLogFile, 'w+')

    komunikat = f"{f_czas()} | {typ} | {zrodlo} | {dane}"

    # wyswietlenie komunikatu w konsoli
    if(typ == "info"):
        print(style.WHITE(komunikat))
    elif(typ == "warn"):
        print(style.YELLOW(komunikat))
    elif(typ == "error"):
        print(style.RED(komunikat))

    # zapis komunikatu do pliku [pathLogFile]
    plik_logu.write(komunikat + '\n')

    # zamykamy plik logu
    plik_logu.close()


def f_rpc_p135(ip):
    '''RPC port 135'''
    target_ip = ip
    authLevel = RPC_C_AUTHN_LEVEL_NONE
    adresy_ip = ""
    wynik = f"[*] Wykryte adresy sieciowe hosta [{target_ip}]\n"
    try:
        stringBinding = r'ncacn_ip_tcp:%s' % target_ip
        rpctransport = transport.DCERPCTransportFactory(stringBinding)

        portmap = rpctransport.get_dce_rpc()
        portmap.set_auth_level(authLevel)
        portmap.connect()

        objExporter = IObjectExporter(portmap)
        
        bindings = objExporter.ServerAlive2()

        #NetworkAddr = bindings[0]['aNetworkAddr']
        for binding in bindings:
            NetworkAddr = binding['aNetworkAddr']
            #print ("Address: " + NetworkAddr)
            adresy_ip += NetworkAddr + "\n"

        wynik += adresy_ip
    except Exception as error:        
        wynik = "error"

    return wynik


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