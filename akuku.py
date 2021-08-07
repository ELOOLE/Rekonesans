import os
import time
import shlex, subprocess, signal
import argparse
import datetime
import pyfiglet
import json
import urllib.request
import codecs

import re
from re import sub

from json2html import *

from copy import Error

import ssl
from ssl import RAND_add

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from bs4 import BeautifulSoup, SoupStrainer

from random import randrange

from PIL import Image, ImageFont, ImageDraw

##########################################
# plik z zasobami do skanowania
# ---------------------------------------
# odczytujemy generujemy z metasploit
# w nastpujacy sposob
# > services -u -c port,proto,name,info -o /home/user/rand1234
##########################################
path_plik_nmap_msfconsole = ""

##########################################
# plik logu - generowany automatycznie 
# jak nie istnije to zostanie stworzony
# nazywa się jak [path_plik_nmap_msfconsole] 
# z ta roznica, ze rozszerzenie jest *.log
##########################################
path_plik_logu = ""

##########################################
# plik logu - generowany automatycznie 
# jak nie istnije to zostanie stworzony
# nazywa się jak [path_plik_nmap_msfconsole]
#  z ta roznica, ze rozszerzenie jest *.json
##########################################
path_plik_json = ""
# dane do zrzutu danych zwiazane wlasnie z plikiem *.json
data = {}

##########################################
# banner aplikacji
# plik logu jak zostanie utworzony 
# wrzuca ten baner jako pierwsza rzecz
# do jego wynikow
##########################################
baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def f_odczyt_pliku_nmap(plik):
    f_zapis_log("skrypt", f"odczytuje plik z danymi: {plik}", "info") 
    #print(f"{f_czas()} | odczytuje plik z danymi: {plik}")
    otwarty_plik_nmap = open(plik, 'r')

    # licze ile jest lini w pliku z danymi
    line_count = 0
    for line in otwarty_plik_nmap:
        if line != "\n":
            line_count += 1
    otwarty_plik_nmap.close()
    f_zapis_log("skrypt",f"Ilosc zadan do wykonania: {line_count}","info")

    # otwieram ponownie
    otwarty_plik_nmap = open(plik, 'r')
    i = 1

    data['host'] = []
    
    # czytamy linijka po linijce 
    for linijka in otwarty_plik_nmap:
        # rozpoczynamy parsowanie pliku
        # services -u -c port,proto,name,info - o /home/user/rand1234
        wynik = linijka.split(',')
        ip = wynik[0].replace("\"", "").rstrip("\n")
        port = wynik[1].replace("\"", "").rstrip("\n")
        protokol = wynik[2].replace("\"", "").rstrip("\n")
        usluga = wynik[3].replace("\"", "").rstrip("\n")
        opis_nmap = wynik[4].replace("\"", "").rstrip("\n")

        #print(f"({i}/{line_count}) | {f_czas()} | IP: {ip} proto:{protokol} port:{port} usluga: {usluga}")
        f_zapis_log("skrypt",f"({i}/{line_count}) | proto:{protokol} IP:{ip} port:{port} usluga:{usluga}", "info")
        i+=1

        r = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if r.match(ip) is None:
            #print(f"{f_czas()} | Wpis nie zawiera poprawnego adresu IP [{ip}]")
            f_zapis_log("skrypt", f"Wpis nie zawiera poprawnego adresu IP [{ip}]", "info")
        else:
            # pierwsza funkcja socat na określenie hosta
            output_socat = f_socat(ip,port,protokol)

            # curl - odpytuje host i daje info dla wykonania screen shota 
            output_curl1 = f_curl(ip,port,protokol,"http")
            output_curl2 = f_curl(ip,port,protokol,"https")
            
            # screen shot w przypadku kiedy curl zwroci 200, 302, 404
            # robienie screen shota-a            
            try:
                if(" 200 " in str(output_curl1) or " 302 " in str(output_curl1) or " 404 " in str(output_curl1)):
                    nazwa_pliku_http = f_screen_shot_web(ip,port,"http")
            except Exception as er:
                f_zapis_log("skrypt - f_screen_shot_web", f"Wyjatek scr shot http://{ip}:{port} {str(er)}", "error")

            try:
                if(" 200 " in str(output_curl2) or " 302 " in str(output_curl2) or " 404 " in str(output_curl2)):
                    nazwa_pliku_https = f_screen_shot_web(ip,port,"https")
            except Exception as er:
                f_zapis_log("skrypt - f_screen_shot_web", f"Wyjatek scr shot https://{ip}:{port} {str(er)}", "error")
                
            #############
            #output_screen_shot_web = "---"
            #if(" 200 " in str(output_curl) or " 302 " in str(output_curl) or " 404 " in str(output_curl)):
            #    output_screen_shot_web = f_screen_shot_web(ip,port,protokol)

            # zapis do pliku *.json
            data['host'].append({'ip':f'{ip}','port':f'{port}','protokol':f'{protokol}','usluga':f'{usluga}','opis':f'{opis_nmap}','socat':f'{output_socat}','curl':f'{output_curl}','screen_shot':f'{output_screen_shot_web}'})
        
    with open(path_plik_json, 'w') as outfile:
        json.dump(data, outfile)
    
    #'/home/nano/data.txt'
    #infoFromJson = json.loads(data)
    build_direction = "LEFT_TO_RIGHT"
    table_attributes = {"style": "width:100%"}
    #print(json2html.convert(infoFromJson, build_direction=build_direction, table_attributes=table_attributes))
    #print(json2html.convert(json = data, build_direction=build_direction, table_attributes=table_attributes))

    raport_html = open('/home/nano/data.hml', 'w')
    raport_html = json2html.convert(json = data, build_direction=build_direction, table_attributes=table_attributes)

    otwarty_plik_nmap.close()

#######################
# SOCAT 
#######################
def f_socat(ip,port,protokol):
    protokol = str.upper(protokol)
    # buduje polecenie
    cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol}:{ip}:{port},connect-timeout=2 - "
    
    # zapisuje do logu jakie zbudowal polecenie
    f_zapis_log("skrypt",cmd,"info")
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]

    # zapisuje do logu jaki jest wynik polecenia
    f_zapis_log("socat",output,"info")

    return output

#######################
# CURL 
#######################
def f_curl(ip,port,protokol, h_prot):
    if(protokol == "tcp"):
        # budujemy sklanie polecenie curl dla http
        cmd_curl = f"curl -I {h_prot}://{ip}:{port} --max-time 2 --no-keepalive -v"
        
        # zapisujemy zbudowane polecenie do pliku logu
        f_zapis_log("skypt", cmd_curl, "info")

        args1 = shlex.split(cmd_curl)
        ps_cmd_curl1 = subprocess.Popen(args1,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        # wynik wykonania polecenia
        curl_output = ps_cmd_curl1.communicate()[0]
        
        # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
        wynik = curl_output
    else:
        # jezeli [protokol] to UDP zmienna [wynik] zwroci wynik jak ponizej
        wynik = "UDP - pomijam"

    # zapisujemy do logu co zwrocila [f_curl]
    f_zapis_log("curl",wynik,"info")

    return wynik

############################
# pobiera linki ze strony
############################
def f_get_links_from_web(ip,port,protokol):
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

#######################
# DIRB
#######################
def f_dirb(ip,port,h_proto):
    cmd = f"dirb {h_proto}://{ip}:{port} /usr/share/wordlists/dirb/common.txt -f -S" 
    cmd_p = f"{f_czas()} | {cmd}"
    print (cmd_p)
    
    dirb = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = dirb.communicate()[0]

    return output
        
###########################
# SCREEN SHOT of WEB PAGE 
###########################
def f_screen_shot_web (ip,port,protokol):
    czas = datetime.datetime.now()
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.headless = True
    driver = webdriver.Chrome(options=options)

    URL = f"{protokol}://{ip}:{port}"

    driver.get(URL)
    S=lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
    #driver.set_window_size(1200,S('Height'))

    driver.set_window_size(S('Width'),S('Height'))
    #driver.set_window_size(1200,1200)

    nazwa_pliku = path_plik_nmap_msfconsole + "_" + f"{ip}_{port}_{protokol}.png"
    znak_wodny = f"{czas} | Protokol: [{protokol}], adres ip: [{ip}], port: [{port}] | ABW / CSIRT GOV"
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

###########################
# SCREEN SHOT of WEB PAGE2 
###########################
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

    nazwa_pliku = path_plik_nmap_msfconsole + "_" + f"{ip}_{port}_{h_prot}_{dopisek}.png"
    driver.find_element_by_tag_name('body').screenshot(nazwa_pliku)

    print(f"(-screen shot [web]-) | {czas} | {nazwa_pliku}")

    driver.quit()
    return nazwa_pliku

#######################
# URL parser
#######################
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

############################
# f_czas()
# funkcja zwracajaca w 
# wyniku aktualny czas
############################
def f_czas ():
    return datetime.datetime.now()

######################################
# Zapis do logu
# plik w zmiennej: [path_plik_logu] 
######################################
def f_zapis_log(zrodlo, dane, typ):
    # sprawdzam istnienie pliku, jeżeli istnieje dopisze w innym przypadku nadpisze. 
    if(os.path.isfile(path_plik_logu)):
        plik_logu = open(path_plik_logu,'a+')
    else:
        plik_logu = open(path_plik_logu,'w+')
        plik_logu.write(baner)
    
    # budowa komunikatu w celu zapisania do pliku w zmiennej [path_plik_logu] i wyswietlenia na konsoli
    # -------------------------------
    # f_czas() - zwraca aktualny czas
    # typ - informacyjnie, ostrzezenie, blad
    # zrodlo - kto wygenerowal ten komunikat
    # dane - jakie dane zawiera wynik wykonania operacji
    komunikat = f"{f_czas()} | {typ} | {zrodlo} | {dane}"
    
    # wyswietlenie komunikatu w konsoli
    print(komunikat)
    
    # zapis komunikatu do pliku [path_plik_logu]
    plik_logu.write(komunikat)
    
    # zamykamy plik logu
    plik_logu.close()

###########
# MAIN    #
###########
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Rekonesans MM wersja 0.1', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str, help='Podaj sciezke do pliku z adresami')
    #parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_nmap_msfconsole = '/home/nano/test1'
    else:
        path_plik_nmap_msfconsole = args.fin
    
    #plik logu 
    path_plik_logu = path_plik_nmap_msfconsole[:-3] + "log"
    path_plik_json = path_plik_nmap_msfconsole[:-3] + "json"

    # wywołujemy funkcję, która odczyta nam plik linijka po linijce
    f_odczyt_pliku_nmap(path_plik_nmap_msfconsole)
