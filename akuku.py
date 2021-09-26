###############################################################################
## akuku for Linux,Windows... v1.0
## Written by WW
## Copyright 2021
###############################################################################

import os
import time
import shlex, subprocess, signal
import argparse
import datetime
from typing import Counter
import pyfiglet
import json
import urllib.request
from urllib.parse import urlparse
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

# pliki wymagane
import html_parser
import f_file

# dane do zrzutu danych zwiazane wlasnie z plikiem *.json
data = {}

baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def f_odczyt_pliku_nmap(plik):
    f_zapis_log("f_odczyt_pliku_nmap", f"odczytuje plik z danymi: {plik}", "info") 
    line_count = f_file.f_policz_wiersze_w_pliku(plik)
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
            '''OUTPUT'''
            '''socat port 1-65535 TCP i UDP'''
            output_socat = f_socat(ip,port,protokol)
            
            '''cURL: wykrywany linki na stronie'''
            output_curl1 = f_curl(ip,port,protokol,"http")
            output_links_from_web_http = "none"
            if(" 200 " in str(output_curl1) or " 302 " in str(output_curl1) or " 404 " in str(output_curl1)):
                output_links_from_web_http = f_get_links_from_web(ip,port,protokol,"http")
            '''http: screen shot w przypadku kiedy curl zwroci 200, 302, 404, robienie screen shota-a'''
            try:
                if(" 200 " in str(output_curl1) or " 302 " in str(output_curl1) or " 404 " in str(output_curl1)):                
                    output_screen_shot_web_http = f_screen_shot_web(ip,port,"http")   
                else:
                    output_screen_shot_web_http = "none"             
            except Exception as er:
                f_zapis_log("f_odczyt_pliku_nmap/f_screen_shot_web", f"Wyjatek scr shot http://{ip}:{port} {str(er)}", "error")
                output_screen_shot_web_http = "none"
            '''cURL: wykrywany linki na stronie'''
            output_curl2 = f_curl(ip,port,protokol,"https")
            output_links_from_web_https = "none"
            if(" 200 " in str(output_curl2) or " 302 " in str(output_curl2) or " 404 " in str(output_curl2)):
                output_links_from_web_https = f_get_links_from_web(ip,port,protokol,"https")
            '''http: screen shot w przypadku kiedy curl zwroci 200, 302, 404, robienie screen shota-a'''
            try:
                if(" 200 " in str(output_curl2) or " 302 " in str(output_curl2) or " 404 " in str(output_curl2)):
                    output_screen_shot_web_https = f_screen_shot_web(ip,port,"https")
                else:
                    output_screen_shot_web_https = "none"
            except Exception as er:
                f_zapis_log("f_odczyt_pliku_nmap/f_screen_shot_web", f"Wyjatek scr shot https://{ip}:{port} {str(er)}", "error")
                output_screen_shot_web_https = "none"

            '''port 22, ssh mechanizm'''
            output_ssh_mechanizm = "none"
            if(port == "22" or "ssh" in str(opis_nmap).lower):
                output_ssh_mechanizm = f_ssh_mechanizm(ip,port)

            '''port 25, smtp'''
            output_smtp = "none"
            if(port == "25" or "smtp" in str(opis_nmap).lower):
                output_smtp = f_smtp(ip)

            '''port 135, DCERPC'''
            output_dcerpc_p135 = "none"
            if(port == "135"):
                output_dcerpc_p135 = f_rpc_p135(ip)
            
            '''port 139, enum4linux'''
            output_enum4linux = "none"
            if(port == "139"):
                output_enum4linux = f_enum4linux(ip)
            
            ###########################################################################
            # zapis do pliku *.json
            data['host'].append({ip:{
                    'ip':ip,
                    'port':port,
                    'protokol':protokol,
                    'usluga':usluga,
                    'opis':opis_nmap,
                    'socat':f'{output_socat}\n',
                }
            })

            '''port 21, ftp, dodatkowe dzialania'''
            if(port == "21" or "ftp" in str(opis_nmap).lower):
                zalecenia_ftp = f"nmap: (NSE) <i><b>nmap --script ftp* -p{port} -d {ip}</b></i>\n"
                zalecenie_ftp += f"Brute-force: <i><b>hydra -s {port} -C /usr/share/wordlists/ftp-default-userpass.txt -u -f {ip} ftp</b></i>\n"
                zalecenie_ftp += f"Brute-force: <i><b>patator ftp_login host={ip} user=FILE0 0=logins.txt password=asdf -x ignore:mesg='Login incorrect.' -x ignore,reset,retry:code=500</b></i>"
                data['host'].append({ip:{'ftp':{'Dodatkowo&nbsp;można:':f'<p style="color:red;">{zalecenia_ftp}</p>\n'}}})

            '''port 22, ssh, output'''
            if(output_ssh_mechanizm != "none"):
                data['host'].append({ip:{'ssh':{'mechanizm':f'{output_ssh_mechanizm}\n'}}})

            if(port == "22" or "ssh" in str(opis_nmap).lower):
                zalecenia_ssh = f"nmap: (NSE) <i><b>nmap --script ssh-brute -d {ip}</b></i>"
                data['host'].append({ip:{'ssh':{'Dodatkowo&nbsp;można':f'<p style="color:red;">{zalecenia_ssh}</p>\n'}}})

            '''port 23, telnet, dodatkowe dzialania'''
            zalecenia_telnet = f"nmap (NSE) <i><b>nmap --script telnet* -p23 -d {ip}</b></i>"
            if(port == "23"):
                data['host'].append({ip:{'telnet':{'Dodatkowo&nbsp;można':f'<p style="color:red;">{zalecenia_telnet}</p>\n'}}})

            '''port 25, smtp, output''''
            if(port == "25"):
                data['host'].append({ip:{'smtp':{'mechanizm':f'{output_smtp}\n'}}})

            '''cURL, output'''
            if(output_curl1 != "none"):
                data['host'].append({ip:{'curl_http:':f'{output_curl1}\n'}})
            if(output_curl2 != "none"):
                data['host'].append({ip:{'curl_https':f'{output_curl2}\n'}})

            '''cURL, links'''
            if(output_links_from_web_http != "none"):
                data['host'].append({ip:{'links_http':f'{output_links_from_web_http}\n'}})
            if(output_links_from_web_https != "none"):
                data['host'].append({ip:{'links_https':f'{output_links_from_web_https}\n'}})

            '''WEB SCREEN SHOT'''
            if(output_screen_shot_web_http != "none"):
                data['host'].append({ip:{'screen_shot_http':f'<img src="{output_screen_shot_web_http}">'}})
            if(output_screen_shot_web_https != "none"):
                data['host'].append({ip:{'screen_shot_https':f'<img src="{output_screen_shot_web_https}">'}})

            '''port 135, DCE RPC, output'''
            if(output_dcerpc_p135 != "none"):
                data['host'].append({ip:{'dcerpc_p135':f'{output_dcerpc_p135}\n'}})

            '''port 139 i 445, enum4linux SMB'''
            if(output_enum4linux != "none"):
                data['host'].append({ip:{'enum4linux':f'{output_enum4linux}\n'}})

    with open(path_plik_json, 'a+') as outfile:
        json.dump(data, outfile)

    try:
        raport_html = open(path_plik_html, 'w')
        raport_html.write(json2html.convert(json = data, table_attributes='width="100%"', clubbing=True, encode=False, escape=True))
        raport_html.close()
        html_parser.f_html_parser(path_plik_html)
    except Exception as e:
        f_zapis_log("f_odczyt_pliku_nmap-raport_html",e,"error")

    otwarty_plik_nmap.close()

def f_ssh_mechanizm(ip, port):
    '''SSH'''
    # buduje polecenie
    cmd = f'nmap --script "ssh* and not ssh-brute" {ip} -p22'
    
    # zapisuje do logu jakie zbudowal polecenie
    f_zapis_log("f_ssh_mechanizm",cmd,"info")
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = str(ps.communicate()[0].decode('utf-8'))

    # zapisuje do logu jaki jest wynik polecenia
    f_zapis_log("f_ssh_mechanizm",output,"info")
    
    if(output == "b''"):
        output = "none"
    
    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]

    return output

def f_smtp(ip):
    '''SMTP'''
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

def f_socat(ip,port,protokol):
    '''SOCAT'''
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

def f_curl(ip,port,protokol, h_prot):
    '''cURL'''
    protokol = str.lower(protokol)
    if(protokol == "tcp"):
        # budujemy sklanie polecenie curl dla http
        cmd_curl = f"curl -I {h_prot}://{ip}:{port} --max-time 2 --no-keepalive -v"
        
        # zapisujemy zbudowane polecenie do pliku logu
        f_zapis_log("f_curl", cmd_curl, "info")

        args1 = shlex.split(cmd_curl)
        ps_cmd_curl1 = subprocess.Popen(args1,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        # wynik wykonania polecenia
        curl_output = str(ps_cmd_curl1.communicate()[0].decode('utf-8'))
        
        # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
        output = str(curl_output)
    else:
        # jezeli [protokol] to UDP zmienna [wynik] zwroci wynik jak ponizej
        output = "UDP - pomijam"

    # zapisujemy do logu co zwrocila [f_curl]
    f_zapis_log("f_curl",output,"info")

    return output

def f_get_links_from_web(ip,port,protokol,h_prot):
    '''pobiera linki ze strony'''
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
                spis_linkow_html += link['href'] + "<br />" 

            spis_linkow = spis_linkow[:-2]
            spis_linkow_html = spis_linkow_html[:-2]

            f_zapis_log("f_get_links_from_web", spis_linkow, "info")
        except Exception as e:
            f_zapis_log("f_get_links_from_web", f"https {e}", "error")
            spis_linkow,spis_linkow_html =  "error"

    return spis_linkow_html[:-2]

def f_enum4linux(ip):
    '''enum4linux'''
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
      
def f_screen_shot_web(ip,port,protokol):
    '''SCREEN SHOT of WEB PAGE '''
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

def f_rpc_p135(ip):
    '''RPC port 135'''
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

def f_czas ():
    '''Zwraca w wyniku aktualny czas'''
    return datetime.datetime.now()

def f_zapis_log(zrodlo, dane, typ):
    '''Zapis wyniku dzialania do pliku logu'''
    '''Sciezka pliku w zmiennej [path_plik_logu]'''
    #sprawdzam istnienie pliku, jeżeli istnieje dopisze w innym przypadku nadpisze '''
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

if __name__ == '__main__':
    '''MAIN'''
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
    
    if(os.path.isfile(path_plik_nmap_msfconsole)):
        '''sprawdza czy plik istnieje'''
        path_plik_logu = path_plik_nmap_msfconsole + ".log"
        path_plik_json = path_plik_nmap_msfconsole + ".json"
        path_plik_html = path_plik_nmap_msfconsole + ".html"

        # wywołujemy funkcję, która odczyta nam plik linijka po linijce
        f_odczyt_pliku_nmap(path_plik_nmap_msfconsole)
    else:
        print("Plik z danymi nie istnieje!" + path_plik_nmap_msfconsole)       
