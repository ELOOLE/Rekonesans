import argparse
import os
import sys

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
        znak_wodny = f"none"
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


####################################################################################################################
if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='censys parser',
        formatter_class=argparse.RawTextHelpFormatter
        )

    parser.add_argument('-fin', '--file-input', action='store', dest='file_input', type=str, 
                        help='Ścieżke do pliku z danymi. Plik źródłowy')
    args = parser.parse_args()

    CURL_MAX_TIME = 7

    if ('file_input' not in args or not args.file_input):
        parser.print_help()
        sys.exit(1)
    else:
        path_file_data = args.file_input

        with open(path_file_data) as file:
            for line in file:
                print(line.rstrip())
                f_screen_shot_web(line.rstrip(), path_file_data)