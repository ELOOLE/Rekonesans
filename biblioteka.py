import os
import subprocess
import datetime
import ssl

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


def f_get_links_from_web(adres):
    '''pobiera linki ze strony'''
    spis_linkow = ""
    spis_linkow_html = ""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        addrHTTP = adres
        f_zapis_log("f_get_links_from_web", addrHTTP, "info")
        parser = 'html.parser'

        resp = urllib.request.urlopen(addrHTTP, context=ctx,timeout=10)
        soup = BeautifulSoup(
            resp, parser, from_encoding=resp.info().get_param('charset'))

        for link in soup.find_all('a', href=True):
            spis_linkow += link['href'] + "\n"
            spis_linkow_html += link['href'] + "<br />"

        #spis_linkow = spis_linkow[:-2]
        #spis_linkow_html = spis_linkow_html[:-2]

        f_zapis_log("f_get_links_from_web", "info", spis_linkow)
    except Exception as e:
        f_zapis_log("f_get_links_from_web", "error", f"{adres} {e}")
        spis_linkow = "error"
        spis_linkow_html = "error"

    return spis_linkow_html


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
    return datetime.datetime.now()

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
        plik_logu = open([pathLogFile], 'a+')
    else:
        plik_logu = open(pathLogFile, 'w+')

    komunikat = f"{f_czas()} | {typ} | {zrodlo} | {dane}"

    # wyswietlenie komunikatu w konsoli
    print(komunikat)

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