from copy import Error
import os
#from re import sub
import re
from ssl import RAND_add
import time
import shlex, subprocess, signal
import argparse
import datetime
import pyfiglet
import codecs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, SoupStrainer
import urllib.request
from random import randrange
import ssl
from PIL import Image, ImageFont, ImageDraw

from selenium.webdriver.chrome.webdriver import WebDriver

# BANNER
baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def socat_cmd(ip,port,protokol):
    protokol = str.upper(protokol)
    cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol}:{ip}:{port},connect-timeout=2 - "

    return cmd

# SOCAT
def rekonesans(ip, protokol, port,usluga):
    czas = datetime.datetime.now()
    
    # czy podany ciag to IP
    r = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    # do zbadania co to jest
    # prawdopodobnie, ze usluga to ssl
    shell_code1 = b'\x15\x03\x03\x00\x02\x02'

    # sprawdzam czy string w zmiennej ip to IP
    if r.match(ip) is None:
        print(f'{czas} | Wpis nie zawiera poprawnego adresu IP [{ip}]')
    else:
        #socat
        cmd_socat = socat_cmd(ip,port,protokol)
        ps_socat = subprocess.Popen(cmd_socat,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        socat_output = ps_socat.communicate()[0]

        if(str(socat_output) == "b''"):
            socat_output = "empty"
        elif(str(shell_code1) in str(socat_output)):
            socat_output += " wykryto usluge SSL"
        else:
            socat_output = str(socat_output)
        
        print(f"1: {str(socat_output)} 2: {str(shell_code1)}" )

        #curl
        if(protokol == "tcp"):
            cmd_curl1 = f"curl -I http://{ip}:{port} --max-time 2 --no-keepalive -v"
            cmd_curl2 = f"curl -I https://{ip}:{port} --max-time 2 --no-keepalive -v -k"

            args1 = shlex.split(cmd_curl1)
            args2 = shlex.split(cmd_curl2)

            ps_cmd_curl1 = subprocess.Popen(args1,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            ps_cmd_curl2 = subprocess.Popen(args2,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            
            curl1_output = ps_cmd_curl1.communicate()[0]
            curl2_output = ps_cmd_curl2.communicate()[0]

            nazwa_pliku_http = ""
            nazwa_pliku_https = ""
            nazwa_pliku_random_http = ""
            nazwa_pliku_random_https = ""
            spis_linkow = ""

            # zrzut linkow
            if(" 200 " in str(curl1_output)):
                try:
                    addrHTTP = f"http://{ip}:{port}/"
                    parser = 'html.parser'
                    resp = urllib.request.urlopen(addrHTTP)
                    soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))

                    for link in soup.find_all('a', href=True):
                        spis_linkow += "\n" + link['href'] 
                        nowy_adres = parsuje_addr(link['href'])

                    print(f"spis_linkow1: {spis_linkow}")
                except Exception as e:
                    print(f"Wyjatek: {e}")

            if(" 200 " in str(curl2_output)):
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                try:
                    addrHTTP = f"https://{ip}:{port}/"
                    parser = 'html.parser'
                    
                    resp = urllib.request.urlopen(addrHTTP, context=ctx)
                    soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))

                    for link in soup.find_all('a', href=True):
                        spis_linkow += "\n" + link['href']
                        nowy_adres = parsuje_addr(link['href'])

                    print(f"spis_linkow2: {spis_linkow}")
                except Exception as e:
                    print(f"Wyjatek: {e}")

            # robienie screen shota-a            
            try:
                if(" 200 " in str(curl1_output)):
                    print(f"Kod 200 {ip} {port}")
                    nazwa_pliku_http = scr_shot_web(ip,port,"http")
                elif(" 302 " in str(curl1_output)):
                    print(f"Kod 302 {ip} {port}")
                    nazwa_pliku_http = scr_shot_web(ip,port,"http")
                elif(" 404 " in str(curl1_output)):
                    print(f"Kod 404 {ip} {port}")
                    nazwa_pliku_http = scr_shot_web(ip,port,"http")
            except Exception as er:
                komunikat = f"Wyjatek scr shot http://{ip}:{port} {str(er)}"
                print(komunikat)
                nazwa_pliku_http = komunikat

            try:
                if(" 200 " in str(curl2_output) or " 302 " in str(curl2_output) or " 404 " in str(curl2_output)):
                    print(f"Kod 200 {ip} {port}")
                    nazwa_pliku_https = scr_shot_web(ip,port,"https")
                elif(" 302 " in str(curl2_output)):
                    print(f"Kod 302 {ip} {port}")
                    nazwa_pliku_https = scr_shot_web(ip,port,"https")
                elif(" 404 " in str(curl2_output)):
                    print(f"Kod 404 {ip} {port}")
                    nazwa_pliku_https = scr_shot_web(ip,port,"https")
            except Exception as er:
                komunikat = f"Wyjatek scr shot https://{ip}:{port} {str(er)}"
                print(komunikat)
                nazwa_pliku_https = komunikat

            wynik = (f"{czas};{ip};{protokol};{port};{usluga};{socat_output};{curl1_output};{curl2_output};{nazwa_pliku_http} | {nazwa_pliku_https} | {nazwa_pliku_random_http} | {nazwa_pliku_random_https};{spis_linkow}")
        else:
            wynik = (f"{czas};{ip};{protokol};{port};{usluga};{socat_output};-;-;-")
        
        plik_wynik.write(wynik+"\n")

def rekonesans_dirb(ip,port,h_proto):
    czas = datetime.datetime.now()
    cmd = f"dirb {h_proto}://{ip}:{port} /usr/share/wordlists/dirb/common.txt -f -S" 
    cmd_p = f"{czas} | {cmd}"
    print (cmd_p)
    
    dirb = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = dirb.communicate()[0]

    return output

def scr_shot_web (ip,port,h_prot):
    czas = datetime.datetime.now()
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.headless = True
    driver = webdriver.Chrome(options=options)

    URL = f"{h_prot}://{ip}:{port}"

    driver.get(URL)
    S=lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    #driver.set_window_size(1200,S('Height'))

    driver.set_window_size(S('Width'),S('Height'))
    #driver.set_window_size(1200,1200)

    nazwa_pliku = plik_z_wynikiem + "_" + f"{ip}_{port}_{h_prot}.png"
    znak_wodny = f"{czas} | Protokol: [{h_prot}], adres ip: [{ip}], port: [{port}] | ABW / CSIRT GOV"
    driver.find_element_by_tag_name('body').screenshot(nazwa_pliku)
    driver.quit()
    
    print(f"(- screen shot web-) | {czas} | {nazwa_pliku}")

    try:
        #nanosimy znak wodny na img
        podpisz_screena = Image.open(nazwa_pliku)
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 13)
        title_text = znak_wodny
        image_editable = ImageDraw.Draw(podpisz_screena)
        wysokosc_img = podpisz_screena.height-29
        szerokosc_img = podpisz_screena.width
        image_editable.rectangle ((0,wysokosc_img+6,szerokosc_img-1,wysokosc_img+21), outline='red', fill='blue')
        image_editable.text((15, wysokosc_img+5), str(title_text), (165,230,211), font=title_font)
        podpisz_screena.save(nazwa_pliku)

        #convert png to jpg
        nazwa_pliku_jpg = nazwa_pliku[:-3] + "jpg"
        img_to_jpg = podpisz_screena.convert('RGB')
        img_to_jpg.save(nazwa_pliku_jpg)

        #skasowac png
        os.remove(nazwa_pliku)
        
        print(f"- Naniesiono podpis na obrazek.\n{nazwa_pliku}")
    except Exception as img_err:
        print(f"Nie podpisano obrazka: \n{img_err} \n{nazwa_pliku}")
    
    return nazwa_pliku

def scr_shot_web2 (ip,port,h_prot,reszta):
    czas = datetime.datetime.now()
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.headless = True
    driver = webdriver.Chrome(options=options)

    URL = f"{h_prot}://{ip}:{port}/{reszta}"    

    dopisek = randrange(1000-10000)

    driver.get(URL)
    S=lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    #driver.set_window_size(1200,S('Height'))

    driver.set_window_size(S('Width'),S('Height'))
    #driver.set_window_size(1200,1200)

    nazwa_pliku = plik_z_wynikiem + "_" + f"{ip}_{port}_{h_prot}_{dopisek}.png"
    driver.find_element_by_tag_name('body').screenshot(nazwa_pliku)

    print(f"(-screen shot [web]-) | {czas} | {nazwa_pliku}")

    driver.quit()
    return nazwa_pliku

def parsuje_addr (adres):
    h_port = ""
    if("https" in adres):
        h_port = "https"
    elif("http" in adres):
        h_port = "http"
    else:
        return "err"

    host = adres[(int(str(adres).find(":")) + 3):]
    host = host[:str(host).find(":")]

    port = adres.split(host)
    port[1]=port[1][1:]

    port =port[1][:str(port[1]).find("/")]

    reszta = adres.split(port)
    reszta = reszta[1]

    return [h_port, host, port, reszta]

def raport_html5(do_pliku):
    raport_wynik_html5.write(do_pliku)

def raport_html5_head():
    raport_wynik_html5.write("<!doctype htmlgt;")
    raport_wynik_html5.write("<head>")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Rekonesans MM wersja 0.1', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str, help='Podaj sciezke do pliku z adresami')
    parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # przypisanie zmiennych podanych przy wywolywaniu skrytpu
    # plik_wczytany - plik z danymi w formacie 
    # services -u -c proto,port,name -o /home/user/Pobrane/dane.txt - tak wygeneruj z msfconsole (metasplita)
    plik_wczytany = args.fin
    # odczyt pliku
    plik = open(plik_wczytany, 'r')

    # plik_z_wynikiem - sciezka do pliku gdzie bedzie sie zapysywal wynik 
    plik_z_wynikiem = args.fout
    
    # raport z rekonesansu w wersji html
    raport_html5_nazwa = plik_z_wynikiem+".hml"
    raport_wynik_html5 = open(raport_html5_nazwa,'w')
    
    # utworzenie pliku
    plik_wynik = open(plik_z_wynikiem,'w')
    # wpisanie pierszej liniki do pliku
    plik_wynik.write("Czas;ip;protokol;port;usluga;socat;curl_http;curl_https;scr_shot;spis_linkow\n")

    # licze ile jest lini w pliku z danymi
    line_count = 0
    for line in plik:
        if line != "\n":
            line_count += 1
   
    plik.close()
    plik = open(plik_wczytany, 'r')

    print("Ilosc zadan do wykonania: {}".format(line_count))

    i = 1
    
    for linijka in plik.readlines():
        Czas = datetime.datetime.now()
        wynik = linijka.split(',')
        ip = wynik[0].replace("\"", "").rstrip("\n")
        protokol = wynik[1].replace("\"", "").rstrip("\n")
        port = wynik[2].replace("\"", "").rstrip("\n")
        usluga = wynik[3].replace("\"", "").rstrip("\n")

        print(f"({i}/{line_count}) | {Czas} | IP:{ip} proto:{protokol} port:{port} usluga:{usluga}")
        i += 1 
        rekonesans(ip,protokol,port,usluga)

    plik.close()
    plik_wynik.close()
    raport_wynik_html5.close()
