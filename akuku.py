import os
import time
import shlex, subprocess, signal
import argparse
import datetime
from typing import Counter
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

import sys, getopt
from impacket.dcerpc.v5 import transport
from impacket.dcerpc.v5.ndr import NULL
from impacket.dcerpc.v5.rpcrt import RPC_C_AUTHN_LEVEL_NONE
from impacket.dcerpc.v5.dcomrt import IObjectExporter

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
# plik json - generowany automatycznie 
# jak nie istnije to zostanie stworzony
# nazywa się jak [path_plik_nmap_msfconsole]
#  z ta roznica, ze rozszerzenie jest *.json
##########################################
path_plik_json = ""
# dane do zrzutu danych zwiazane wlasnie z plikiem *.json
data = {}

##########################################
# plik html - generowany z pliku *.json 
# nazywa się jak [path_plik_nmap_msfconsole]
#  z ta roznica, ze rozszerzenie jest *.html
##########################################
path_plik_html = ""

##########################################
# banner aplikacji
# plik logu jak zostanie utworzony 
# wrzuca ten baner jako pierwsza rzecz
# do jego wynikow
##########################################
baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def f_odczyt_pliku_nmap(plik):
    f_zapis_log("f_odczyt_pliku_nmap", f"odczytuje plik z danymi: {plik}", "info") 
    #print(f"{f_czas()} | odczytuje plik z danymi: {plik}")
    otwarty_plik_nmap = open(plik, 'r')

    # licze ile jest lini w pliku z danymi
    line_count = 0
    for line in otwarty_plik_nmap:
        if line != "\n":
            line_count += 1
    otwarty_plik_nmap.close()
    f_zapis_log("f_odczyt_pliku_nmap",f"Ilosc zadan do wykonania: {line_count}","info")

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
        f_zapis_log("-----------", "-----------------------------------------------------------------", "-------")
        f_zapis_log("f_odczyt_pliku_nmap",f"({i}/{line_count}) | proto:{protokol} IP:{ip} port:{port} usluga:{usluga}", "info")
        i+=1

        r = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if r.match(ip) is None:
            f_zapis_log("f_odczyt_pliku_nmap", f"Wpis nie zawiera poprawnego adresu IP [{ip}]", "info")
        else:
            # OUTPUT
            # socat
            output_socat = f_socat(ip,port,protokol)

            # OUTPUT
            # curl - odpytuje host i daje info dla wykonania screen shota 
            # http
            output_curl1 = f_curl(ip,port,protokol,"http")
            # https
            output_curl2 = f_curl(ip,port,protokol,"https")
            
            # ----------------------------------------------------------
            # wykrywany linki na stronie
            output_links_from_web_http = "none"
            if(" 200 " in str(output_curl1) or " 302 " in str(output_curl1) or " 404 " in str(output_curl1)):
                output_links_from_web_http = f_get_links_from_web(ip,port,protokol,"http")
            output_links_from_web_https = "none"
            if(" 200 " in str(output_curl2) or " 302 " in str(output_curl2) or " 404 " in str(output_curl2)):
                output_links_from_web_https = f_get_links_from_web(ip,port,protokol,"https")                

            # ----------------------------------------------------------
            # screen shot w przypadku kiedy curl zwroci 200, 302, 404
            # robienie screen shota-a     
            # http    
            try:
                if(" 200 " in str(output_curl1) or " 302 " in str(output_curl1) or " 404 " in str(output_curl1)):                
                    output_screen_shot_web_http = f_screen_shot_web(ip,port,"http")   
                else:
                    output_screen_shot_web_http = "none"             
            except Exception as er:
                f_zapis_log("f_odczyt_pliku_nmap/f_screen_shot_web", f"Wyjatek scr shot http://{ip}:{port} {str(er)}", "error")
                output_screen_shot_web_http = "none"
            
            # https
            try:
                if(" 200 " in str(output_curl2) or " 302 " in str(output_curl2) or " 404 " in str(output_curl2)):
                    output_screen_shot_web_https = f_screen_shot_web(ip,port,"https")
                else:
                    output_screen_shot_web_https = "none"
            except Exception as er:
                f_zapis_log("f_odczyt_pliku_nmap/f_screen_shot_web", f"Wyjatek scr shot https://{ip}:{port} {str(er)}", "error")
                output_screen_shot_web_https = "none"

            # OUTPUT
            # DCERPC port 135
            output_dcerpc_p135 = "none"
            if(port == "135"):
                output_dcerpc_p135 = f_rpc_p135(ip)

            # enum4linux
            output_enum4linux = "none"
            if(port == "139"):
                output_enum4linux = f_enum4linux(ip)

            # ssh mechanizm
            output_ssh_mechanizm = "none"
            if(port == "22"):
                output_ssh_mechanizm = f_ssh_mechanizm(ip)

            # port 25
            # smtp
            output_smtp = "none"
            if(port == "25"):
                output_smtp = f_smtp(ip)

            ########################################################################333

            # zapis do pliku *.json
            data['host'].append({
                ip:{
                    'ip':ip,
                    'port':port,
                    'protokol':protokol,
                    'usluga':usluga,
                    'opis':opis_nmap,
                    'socat':f'{output_socat}\n',
                }
            })

            # CURL
            if(output_curl1 != "none"):
                data['host'].append({ip:{'curl_http:':f'{output_curl1}\n'}})
            if(output_curl2 != "none"):
                data['host'].append({ip:{'curl_https':f'{output_curl2}\n'}})

            # LINKS
            if(output_links_from_web_http != "none"):
                data['host'].append({ip:{'links_http':f'{output_links_from_web_http}\n'}})
            if(output_links_from_web_https != "none"):
                data['host'].append({ip:{'links_https':f'{output_links_from_web_https}\n'}})

            # WEB SCREEN SHOT
            if(output_screen_shot_web_http != "none"):
                data['host'].append({ip:{'screen_shot_http':f'<img src="{output_screen_shot_web_http}">'}})
            if(output_screen_shot_web_https != "none"):
                data['host'].append({ip:{'screen_shot_https':f'<img src="{output_screen_shot_web_https}">'}})

            # port 22
            # ssh mechanizm
            if(output_ssh_mechanizm != "none"):
                data['host'].append({ip:{'ssh':{'mechanizm':f'{output_ssh_mechanizm}\n'}}})

            zalecenia_ssh = f"nmap: (NSE) <i><b>nmap --script ssh-brute -d {ip}</b></i>"
            if(port == "22"):
                data['host'].append({ip:{'ssh':{'zalecane':f'{zalecenia_ssh}\n'}}})
# 58775
            # port 23
            # telnet
            zalecenia_telnet = f"nmap (NSE) <i><b>nmap --script *telnet* -p23 -d {ip}</b></i>"
            if(port == "23"):
                data['host'].append({ip:{'telnet':{'zalecane':f'{zalecenia_telnet}\n'}}})

            # port 25
            # smtp
            if(port == "25"):
                data['host'].append({ip:{'smtp':{'mechanizm':f'{output_smtp}\n'}}})

            # port 135
            # DCE RPC 
            if(output_dcerpc_p135 != "none"):
                data['host'].append({ip:{'dcerpc_p135':f'{output_dcerpc_p135}\n'}})

            # port 139 i 445
            # enum4linux SMB
            if(output_enum4linux != "none"):
                data['host'].append({ip:{'enum4linux':f'{output_enum4linux}\n'}})

    with open(path_plik_json, 'a+') as outfile:
        json.dump(data, outfile)

    try:
        raport_html = open(path_plik_html, 'w')
        raport_html.write(json2html.convert(json = data, table_attributes='width="100%"', clubbing=True, encode=False, escape=True))
        raport_html.close()
    except Exception as e:
        f_zapis_log("f_odczyt_pliku_nmap-raport_html",e,"error")

    otwarty_plik_nmap.close()

#############
# SSH       #
#############
def f_ssh_mechanizm(ip):
    # buduje polecenie
    cmd = f'nmap --script "ssh* and not ssh-brute" {ip} -p22'
    
    # zapisuje do logu jakie zbudowal polecenie
    f_zapis_log("f_ssh_mechanizm",cmd,"info")
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = str(ps.communicate()[0])

    # zapisuje do logu jaki jest wynik polecenia
    f_zapis_log("f_ssh_mechanizm",output,"info")
    
    if(output == "b''"):
        output = "none"
    
    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]

    return output

#############
# SSH       #
#############
def f_smtp(ip):
    # buduje polecenie
    cmd = f'nmap --script smtp* -p25 {ip}'
    
    # zapisuje do logu jakie zbudowal polecenie
    f_zapis_log("f_smtp",cmd,"info")
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = str(ps.communicate()[0])

    # zapisuje do logu jaki jest wynik polecenia
    f_zapis_log("f_smtp",output,"info")
    
    if(output == "b''"):
        output = "none"
    
    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]

    return output

#############
# SOCAT     #
#############
def f_socat(ip,port,protokol):
    protokol = str.upper(protokol)
    # buduje polecenie
    cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol}:{ip}:{port},connect-timeout=2 - "
    
    # zapisuje do logu jakie zbudowal polecenie
    f_zapis_log("f_socat",cmd,"info")
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = str(ps.communicate()[0])

    # zapisuje do logu jaki jest wynik polecenia
    f_zapis_log("socat",output,"info")
    
    if(output == "b''"):
        output = "none"
    
    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]

    return output

#############
# CURL      #
#############
def f_curl(ip,port,protokol, h_prot):
    if(protokol == "tcp"):
        # budujemy sklanie polecenie curl dla http
        cmd_curl = f"curl -I {h_prot}://{ip}:{port} --max-time 2 --no-keepalive -v"
        
        # zapisujemy zbudowane polecenie do pliku logu
        f_zapis_log("f_curl", cmd_curl, "info")

        args1 = shlex.split(cmd_curl)
        ps_cmd_curl1 = subprocess.Popen(args1,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        # wynik wykonania polecenia
        curl_output = str(ps_cmd_curl1.communicate()[0])
        
        # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
        output = str(curl_output)
    else:
        # jezeli [protokol] to UDP zmienna [wynik] zwroci wynik jak ponizej
        output = "UDP - pomijam"

    if(output == "b''"):
        output = "none"
    
    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]

    # zapisujemy do logu co zwrocila [f_curl]
    f_zapis_log("f_curl",output,"info")

    return output

############################
# pobiera linki ze strony
############################
def f_get_links_from_web(ip,port,protokol,h_prot):
    spis_linkow = ""
    spis_linkow_html = ""
    # zrzut linkow
    if(h_prot == "http"):
        try:
            addrHTTP = f"http://{ip}:{port}/"
            f_zapis_log("f_get_links_from_web", addrHTTP,"info")
            parser = 'html.parser'
            resp = urllib.request.urlopen(addrHTTP)
            soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))

            for link in soup.find_all('a', href=True):
                spis_linkow += link['href'] + "\n"
                spis_linkow_html += link['href'] + "<br />" 
                #nowy_adres = parsuje_addr(link['href'])
                #linki['url'].append({link['href']})

            spis_linkow = spis_linkow[:-2]
            spis_linkow_html = spis_linkow_html[:-2]

            f_zapis_log("f_get_links_from_web", spis_linkow, "info")
        except Exception as e:
            f_zapis_log("f_get_links_from_web", f"http {e}", "error")
            spis_linkow,spis_linkow_html = f"error: {e}"
    elif(h_prot == "https"):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        try:
            addrHTTP = f"https://{ip}:{port}/"
            f_zapis_log("f_get_links_from_web", addrHTTP,"info")
            parser = 'html.parser'
            
            resp = urllib.request.urlopen(addrHTTP, context=ctx)
            soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))

            for link in soup.find_all('a', href=True):
                spis_linkow += link['href'] + "\n"
                #nowy_adres = parsuje_addr(link['href'])
                spis_linkow_html += link['href'] + "<br />" 

            spis_linkow = spis_linkow[:-2]
            spis_linkow_html = spis_linkow_html[:-2]

            f_zapis_log("f_get_links_from_web", spis_linkow, "info")
        except Exception as e:
            f_zapis_log("f_get_links_from_web", f"https {e}", "error")
            spis_linkow,spis_linkow_html =  "error"

    return spis_linkow_html[:-2]

##############
# enum4linux #
##############
def f_enum4linux(ip):
    # buduje polecenie
    cmd = f"enum4linux {ip}"
    
    # zapisuje do logu jakie zbudowal polecenie
    f_zapis_log("f_enum4linux",cmd,"info")
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = str(ps.communicate()[0])

    # zapisuje do logu jaki jest wynik polecenia
    f_zapis_log("enum4linux",output,"info")
    
    if(output == "b''"):
        output = "none"
    
    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]

    return output

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
def f_screen_shot_web(ip,port,protokol):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.headless = True
        driver = webdriver.Chrome(options=options)

        URL = f"{protokol}://{ip}:{port}"
        f_zapis_log("f_screen_shot_web", URL, "info")

        driver.get(URL)
        S=lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
        #driver.set_window_size(1200,S('Height'))

        driver.set_window_size(S('Width'),S('Height'))
        #driver.set_window_size(1200,1200)

        # nazwa pliku *.png
        nazwa_pliku = path_plik_nmap_msfconsole + "_" + f"{ip}_{port}_{protokol}.png"
        f_zapis_log("f_screen_shot_web", f"nazwa pliku screen shot-a {nazwa_pliku}", "info")

        # treść znaku wodnego nanoszonego na *.png
        znak_wodny = f"{f_czas()} | Protokol: [{protokol}], adres ip: [{ip}], port: [{port}]"
        f_zapis_log("f_screen_shot_web", f"znak wodny {znak_wodny}", "info")

        driver.find_element_by_tag_name('body').screenshot(nazwa_pliku)
        driver.quit()
    except Exception as error:
        f_zapis_log("f_screen_shot_web", error, "error")
    
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
        f_zapis_log("f_screen_shot_web", f"Naniesiono podpis na obrazek: {nazwa_pliku}", "info")

        #convert png to jpg
        nazwa_pliku_jpg = nazwa_pliku[:-3] + "jpg"
        img_to_jpg = podpisz_screena.convert('RGB')
        img_to_jpg.save(nazwa_pliku_jpg)
        f_zapis_log("f_screen_shot_web", f"konversja {nazwa_pliku} -> {nazwa_pliku_jpg}", "info")

        #skasowac png
        os.remove(nazwa_pliku)
        f_zapis_log("f_screen_shot_web", f"skanowano plik {nazwa_pliku}", "info")
    except Exception as img_err:
        f_zapis_log("f_screen_shot_web", f"Nie podpisano obrazka dla {protokol}://{ip}:{port} {img_err} ", "error")

    return nazwa_pliku_jpg

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

def f_rpc_p135(ip):
    target_ip = ip
    authLevel = RPC_C_AUTHN_LEVEL_NONE
    adresy_ip = ""
    wynik = f"[*] Wykryte adresy sieciowe hosta [{target_ip}]\n"
    
    stringBinding = r'ncacn_ip_tcp:%s' % target_ip
    rpctransport = transport.DCERPCTransportFactory(stringBinding)

    portmap = rpctransport.get_dce_rpc()
    portmap.set_auth_level(authLevel)
    portmap.connect()

    objExporter = IObjectExporter(portmap)
    bindings = objExporter.ServerAlive2()

    #print (" " + target_ip)
    f_zapis_log("f_rpc_p135",f"[*] Wykryte adresy sieciowe hosta[{target_ip}]","info")
    
    #NetworkAddr = bindings[0]['aNetworkAddr']
    for binding in bindings:
        NetworkAddr = binding['aNetworkAddr']
        #print ("Address: " + NetworkAddr)
        adresy_ip += NetworkAddr + "\n"
    
    wynik += adresy_ip
    f_zapis_log("f_rpc_p135",adresy_ip,"info") 
    return wynik

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
    plik_logu.write(komunikat+'\n')
    
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
        path_plik_nmap_msfconsole = '/home/user/test1'
    else:
        path_plik_nmap_msfconsole = args.fin
    
    #plik logu 
    path_plik_logu = path_plik_nmap_msfconsole + ".log"
    path_plik_json = path_plik_nmap_msfconsole + ".json"
    path_plik_html = path_plik_nmap_msfconsole + ".html"

    # wywołujemy funkcję, która odczyta nam plik linijka po linijce
    f_odczyt_pliku_nmap(path_plik_nmap_msfconsole)
