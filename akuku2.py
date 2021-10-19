###############################################################################
## akuku for Linux,Windows... v0.2
## Written by MM
## Copyright 2021
## input: metasploit(db_nmap - discover)         
## services -u -c port,proto,name,info -o /home/user/rand1234
###############################################################################

import os
import socket
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
from ssl import CertificateError, RAND_add

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

# dane do zrzutu danych zwiazane wlasnie z plikiem *.json
ilosc_uslug = 0

baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def f_odczyt_pliku_nmap(plik):
    f_zapis_log("f_odczyt_pliku_nmap", f"odczytuje plik z danymi: {plik}", "info") 
    line_count = f_policz_wiersze_w_pliku(plik)
    f_zapis_log("f_odczyt_pliku_nmap",f"Ilosc zadan do wykonania: {line_count}","info")

    global ilosc_uslug
    ilosc_uslug = line_count

    tips_color = "blue"
    # otwieram ponownie
    otwarty_plik_nmap = open(plik, 'r')
    i = 1
    data = {}
    data['skan'] = []

    # czytamy linijka po linijce 
    for linijka in otwarty_plik_nmap:
        # rozpoczynamy parsowanie pliku
        wynik = linijka.split(',')
        ip = wynik[0].replace("\"", "").rstrip("")
        port = wynik[1].replace("\"", "").rstrip("")
        protokol = wynik[2].replace("\"", "").rstrip("")
        usluga = wynik[3].replace("\"", "").rstrip("")
        opis_nmap = wynik[4].replace("\"", "").rstrip("")

        #print(f"({i}/{line_count}) | {f_czas()} | IP: {ip} proto:{protokol} port:{port} usluga: {usluga}")
        f_zapis_log("---------", "-----------------------------------------------------------------", "-------------------")
        f_zapis_log("f_odczyt_pliku_nmap",f"({i}/{line_count}) | proto:{protokol} IP:{ip} port:{port} usluga:{usluga}", "info")

        r = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if r.match(ip) is None:
            f_zapis_log("f_odczyt_pliku_nmap", f"Wpis nie zawiera poprawnego adresu IP [{ip}]", "info")
            ilosc_uslug -= 1
        else:
            # zapis do pliku *.json
            tmp_dict = {ip:{
                    'ip':ip,
                    'port':port,
                    'protokol':protokol,
                    'usluga':usluga,
                    'opis':opis_nmap
                }}
           
            ######################################################
            #socat port 1-65535 TCP i UDP
            output_socat = f_socat(ip,port,protokol)
            if(output_socat != "none"):
                tmp_dict[ip]['socat'] = f'{output_socat}\n'

            ######################################################
            # cURL, links, web_shot
            # lista_protokol
            lista_protokol = ["http","https"]
            # petla 2-elementowa z listy lista_protokol
            for h_prot in lista_protokol:
                #output_curl
                output_curl = f_curl(ip,port,protokol,h_prot)
                if(output_curl != "none"):
                    # zapis do pliku *.json
                    tmp_dict[ip][f'curl:{h_prot}'] = f'{output_curl}\n'
                
                    # zmienna adres
                    adres = f"{h_prot}://{ip}:{port}"
                    # zapis do logu podstalej zmiennej adres
                    f_zapis_log("f_odczyt_pliku_nmap", f"adres [{adres}]", "info")

                    # sprawdzamy wynik curl
                    http_code = f_curl_variables(adres, "http_code")
                    # zapis do logu
                    f_zapis_log("f_odczyt_pliku_nmap", f"http_code: [{http_code}]", "info")

                    # warunek 
                    # 000 - wyswietla strone
                    # 200 - wyswietla strone
                    # 301 - Moved Permanently
                    # 302 - przekierowanie
                    # 404 - wyswietla strone, ze nie ma podanej strony      
                    if(http_code == "000" or http_code == "200" or http_code == "301" or http_code == "302" or http_code == "404"):                
                        try:
                            #warunek, jezeli przekierwoanie
                            if(http_code == "301"):
                                # wynik funkcji, ktory sprawdza na jaki adres przekierowuje
                                adres = f_curl_variables(adres, "redirect_url")
                                # zapis do logu
                                f_zapis_log("f_odczyt_pliku_nmap", f"adres [{adres}]", "info")
                                
                                adres2 = adres + f_curl_variables_JS(adres)
                                if(adres2 != "none"):
                                    adres = adres2
                            
                            output_links_from_web = f_get_links_from_web(adres)
                            
                            # zapis do pliku *.json
                            tmp_dict[ip][f'links:{h_prot}'] = f'{output_links_from_web}\n'
                            output_screen_shot_web = f_screen_shot_web(adres)
                            if(output_screen_shot_web == "error"):
                                # zapis do pliku *.json
                                tmp_dict[ip][f'web_shot:'] = f'{output_screen_shot_web}\n'
                            else:
                                # zapis do pliku *.json
                                tmp_dict[ip][f'web_shot:'] = f'<img src="{output_screen_shot_web}">\n'
                        except Exception as er:
                            f_zapis_log("f_odczyt_pliku_nmap/f_screen_shot_web", f"Wyjatek scr shot {h_prot}://{ip}:{port} {str(er)}", "error")
                            output_screen_shot_web = "none"
                        
                        # zapis do pliku *.json
                        tmp_dict[ip]['wskazowka:nikto'] = f'nikto -h {ip}\n'
                        tmp_dict[ip]['wskazowka:dirb'] = f'dirb {h_prot}://{ip} /usr/share/wordlists/dirb/common.txt\n'
            
            # ports / services    
            # port 21
            if(port == "21" or "ftp" in opis_nmap.lower()):
                # zapis do pliku *.json
                tmp_dict[ip]['wskazowka:[NSE]:nmap'] = f'nmap --script ftp* -p{port} -d {ip}\n'
                tmp_dict[ip]['wskazowka:[Brute-force]:hydra'] = f'hydra -s {port} -C /usr/share/wordlists/ftp-default-userpass.txt -u -f {ip} ftp\n'
                tmp_dict[ip]['wskazowka:[Brute-force]:patator'] = f"patator ftp_login host={ip} user=FILE0 0=logins.txt password=asdf -x ignore:mesg='Login incorrect.' -x ignore,reset,retry:code=500"

            # port 22
            #output_ssh_mechanizm = "none"
            if(port == "22" or "ssh" in opis_nmap.lower()):
                output_ssh_mechanizm = f_ssh_mechanizm(ip,port)
                # zapis do pliku *.json
                tmp_dict[ip]['ssh'] = f'{output_ssh_mechanizm}\n'
                # zapis do pliku *.json
                tmp_dict[ip]['wskazowka:[NSE]:nmap'] = f'nmap --script ssh-brute -d {ip}'
                tmp_dict[ip]['wskazowka:[Brute-force]:patator'] = f"patator ssh_login host={ip} user=FILE0 0=logins.txt password=$(perl -e ""print 'A'x50000"") --max-retries 0 --timeout 10 -x ignore:time=0-3"
                tmp_dict[ip]['wskazowka:[Brute-force]:info'] = f"Brute-force uslugi ssh z powodu ograniczen ilosciowych zapytan, zaleca sie uzyc malego slownika"

            # port 23
            if(port == "23" or "telnet" in opis_nmap.lower()):
                # zapis do pliku *.json
                tmp_dict[ip]['wskazowka:[NSE]:nmap'] = f"nmap --script telnet* -p23 -d {ip}"
                
            # port 25
            # output_smtp = "none"
            if(port == "25" or "smtp" in opis_nmap.lower()):
                output_smtp = f_smtp(ip)
                # zapis do pliku *.json
                tmp_dict[ip]['smtp'] = f'{output_smtp}\n'
                tmp_dict[ip]['wskazowka:enum1'] = f"smtp-user-enum -M VRFY -U users.txt -t {ip}"
                tmp_dict[ip]['wskazowka:enum2'] = f"smtp-user-enum -M EXPN -u admin1 -t {ip}"
                tmp_dict[ip]['wskazowka:enum3'] = f"smtp-user-enum.pl -M RCPT -U users.txt -T mail-server-ips.txt {ip}"
                tmp_dict[ip]['wskazowka:enum4'] = f"smtp-user-enum.pl -M EXPN -D example.com -U users.txt -t {ip}"

           
            # port 53, dns
            if(port == "53"):
                # zapis do pliku *.json
                tmp_dict[ip]['wskazowka:dnsrecon'] = f"dnsrecon -w -g -d {ip} --csv /home/user/dnsrecon{ip}.csv</b> do zapisu, musi byc podana sciezna bezwzgledna inaczej nie zapisze"
                tmp_dict[ip]['wskazowka:dnsenum'] = f"dnsenum --noreverse {ip}"
                
            # port 67, 68, DHCP protocol: UDP
            
            # port 110, pop3
            
            # port 123, NTP, protocol: UDP
            
            # port 135
            #output_dcerpc_p135 = "none"
            if(port == "135"):
                output_dcerpc_p135 = f_rpc_p135(ip)
                # zapis do pliku *.json
                tmp_dict[ip]['dcerpc'] = f'{output_dcerpc_p135}'
            
            # port 137
            
            # port 139, enum4linux
            #output_enum4linux = "none"
            if(port == "139"):
                output_enum4linux = f_enum4linux(ip)
                # zapis do pliku *.json
                tmp_dict[ip]['dcerpc'] = f'{output_enum4linux}'
            
            # port 143 imap
            
            # port 161
            
            # port 512
            
            # port 513
            
            # port 514
            
            # 543 klogin, Kerberos login
            # 544 kshell, Kerberos Remote shell
            # 546 DHCPv6 client
            # 547 DHCPv6 server
            i+=1
            data['skan'].append(tmp_dict)
    ###########################################################################
    #with open(path_plik_json, 'a+') as outfile:
    #    json.dump(data, outfile)

    # zapisuje dane do pliku *.json
    f_zapisz_dane_jako_json(data, path_plik_json)

    # zapisuje dane do pliku *.html
    f_parsuj_dane_json_na_html(data, path_plik_html)
    
    #try:
    #    raport_html = open(path_plik_html, 'w')
    #    raport_html.write(json2html.convert(json = data, table_attributes='width="100%"', clubbing=True, encode=False, escape=True))
    #    raport_html.close()
    #    f_html_parser(path_plik_html)
    #except Exception as e:
    #    f_zapis_log("f_odczyt_pliku_nmap-raport_html",e,"error")

    otwarty_plik_nmap.close()

# SOCAT
def f_socat(ip,port,protokol):
    '''SOCAT'''
    protokol = str.upper(protokol)
    # buduje polecenie
    cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol}:{ip}:{port},connect-timeout=2 - "
    
    # zapisuje do logu jakie zbudowal polecenie
    f_zapis_log("f_socat",cmd,"info")
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = str(ps.communicate()[0])
    
    if(output == "b''"):
        output = "none"
    
    if(output[:2] == "b'"):
        output = output[2:-1]
    elif(output[:2] == 'b"'):
        output = output[2:-1]

    # zapisuje do logu jaki jest wynik polecenia
    f_zapis_log("socat:output",output,"info")
    
    return output    
    
def f_ssh_mechanizm(ip, port):
    '''SSH'''
    # buduje polecenie
    cmd = f'nmap --script "ssh* and not ssh-brute and not ssh-run" {ip} -p22'
    
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

def f_curl(ip,port,protokol, h_prot):
    '''cURL'''
    protokol = str.lower(protokol)
    if(protokol == "tcp"):
        # budujemy sklanie polecenie curl dla http
        if(h_prot == "http"):
            cmd_curl = f"curl -I -k {h_prot}://{ip}:{port} --max-time 2 --no-keepalive -v"
        elif(h_prot == "https"):
            cmd_curl = f"curl -I -k {h_prot}://{ip}:{port} --max-time 2 --no-keepalive -v"

        # zapisujemy zbudowane polecenie do pliku logu
        f_zapis_log("f_curl", cmd_curl, "info")

        args1 = shlex.split(cmd_curl)
        ps_cmd_curl1 = subprocess.Popen(args1,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        # wynik wykonania polecenia
        curl_output = str(ps_cmd_curl1.communicate()[0].decode('utf-8'))
        
        # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
        output = str(curl_output).strip()
        if(len(output) == 0):
            output = "none"
    else:
        # jezeli [protokol] to UDP zmienna [wynik] zwroci wynik jak ponizej
        output = "none"

    # zapisujemy do logu co zwrocila [f_curl]
    f_zapis_log("f_curl",output,"info")

    return output.strip()

def f_curl_variables(addr, parametr):
    # budujemy polecenie
    cmd_curl = "curl --silent --write-out %{" + parametr + "}" + f" --output /dev/null {addr}"

    # zapisujemy zbudowane polecenie do pliku logu
    f_zapis_log("f_curl_variables", cmd_curl, "info")

    args1 = shlex.split(cmd_curl)
    ps_cmd_curl1 = subprocess.Popen(args1,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    # wynik wykonania polecenia
    curl_output = str(ps_cmd_curl1.communicate()[0].decode('utf-8'))
    
    # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
    output = str(curl_output).strip()
    if(len(output) == 0):
        output = "none"

    # zapisujemy do logu co zwrocila [f_curl]
    f_zapis_log("f_curl",output,"info")

    return output

def f_curl_variables_JS(addr):
    # budujemy polecenie
    cmd_curl = f"curl -Lks {addr} | grep window "

    # zapisujemy zbudowane polecenie do pliku logu
    f_zapis_log("f_curl_variables_JS", cmd_curl, "info")

    args1 = shlex.split(cmd_curl)
    ps_cmd_curl1 = subprocess.Popen(args1,shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    # wynik wykonania polecenia
    curl_output = str(ps_cmd_curl1.communicate()[0].decode('utf-8'))
    
   # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
    output = str(curl_output).strip()
    output_window = output.split("\n")
    link_addr = ""

    for x in output_window:
        if("window" in x):
            link_addr = x
    
    start = link_addr.find("/")
    end = link_addr[start:].find('"') + start

    output = link_addr[start+1:end]
    
    if(len(output) == 0):
        output = "none"

    f_zapis_log("f_curl",output,"info")

    return output

def f_get_links_from_web(adres):
    '''pobiera linki ze strony'''
    spis_linkow = ""
    spis_linkow_html = ""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        addrHTTP = adres
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
        f_zapis_log("f_get_links_from_web", f"{adres} {e}", "error")
        spis_linkow =  "error"
        spis_linkow_html =  "error"

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
      
def f_screen_shot_web(adres):
    '''SCREEN SHOT of WEB PAGE '''
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.headless = True
        driver = webdriver.Chrome(options=options)

        lista_adres = urlparse(adres)
        
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
        URL = adres
        f_zapis_log("f_screen_shot_web", URL, "info")

        driver.get(URL)
        S=lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
        #driver.set_window_size(1200,S('Height'))

        driver.set_window_size(S('Width'),S('Height'))
        #driver.set_window_size(1200,1200)

        # nazwa pliku *.png
        nazwa_pliku = path_plik_nmap_msfconsole + "_" + f"{ip}_{port}_{protokol}.png"
        f_zapis_log("f_screen_shot_web", f"nazwa pliku screen shot-a {nazwa_pliku}", "info")

        # tresc znaku wodnego nanoszonego na *.png
        znak_wodny = f"{f_czas()} | Protokol: [{protokol}], adres ip: [{ip}], port: [{port}]"
        f_zapis_log("f_screen_shot_web", f"znak wodny {znak_wodny}", "info")

        #driver.find_element_by_tag_name('body').screenshot(nazwa_pliku)
        driver.save_screenshot(nazwa_pliku)
        driver.quit()

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
        obrazek = os.path.basename(nazwa_pliku_jpg)
    except Exception as error:
        f_zapis_log("f_screen_shot_web", error, "error")
        obrazek = "error"
        
    return obrazek

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
    #sprawdzam istnienie pliku, je|eli istnieje dopisze w innym przypadku nadpisze '''
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

def f_count_str_in_file(path, szukana):
    '''liczy ilosc linijek w wierszu'''
    '''zwraca: int, ilosc linijek w podanym pliku'''
    # otwieram plik
    otwarty_plik = open(path, "r")
    data = otwarty_plik.read()
    
    wystapien = data.count(szukana)
    
    otwarty_plik.close()
    # zwracam wynik
    return wystapien

def f_zapisz_dane_jako_json(data, dstfile):
    with open(dstfile, 'a+') as outfile:
        json.dump(data, outfile)

def f_parsuj_dane_json_na_html(data, dstfile):
    try:
        raport_html = open(path_plik_html, 'w')
        raport_html.write(json2html.convert(json = data, table_attributes='width="100%"', clubbing=True, encode=False, escape=True))
        raport_html.close()
        f_html_parser(path_plik_html)
    except Exception as e:
        f_zapis_log("f_odczyt_pliku_nmap-raport_html",e,"error")

def f_html_parser(file_html):
    file_html_new = file_html[:-5] + "_convert.html"

    open_file_html = open(file_html, "r")
    open_file_html_new = open(file_html_new, "w+")

    head = '<!DOCTYPE html> \n'
    head += '<html>\n'
    head += '<head>\n'
    head += '<style>\n'
    head += 'table, th, td {'
    head += 'font-family: "Lucida Console", Monaco, monospace;'
    head += 'border: 1px solid #1C6EA4;'
    head += 'background-color: #EEEEEE;'
    head += 'width: 100%;'
    head += 'text-align: left;'
    head += 'border-collapse: collapse;}'
    head += 'th {text-align: right; width: 5%;}\n'
    head += '</style>\n'
    head += '</head>\n'
    head += '<body>\n'
    head += '<table>\n'
    head += '<tr>\n'
    head += '<td>\n'
    head += '<h5 style="text-align:right">autor: MM, wersja 0.1 2021 r.</h5>\n'
    head += '<hr>\n'
    head += f'<h1 style="text-align:center">Rekonesans {str(ilosc_uslug)} uslug.</h1>\n'
    head += '<hr>\n'
    head += f'SRT: {start_script}<br/>END: {str(f_czas ())}\n'
    head += '<hr>\n'
    head += f'Plik logu: {path_plik_logu}\n'
    head += '<br />\n'
    head += f'Bledow w pliku logu: {f_count_str_in_file(path_plik_logu, "error")}\n'
    head += '</td>\n'
    head += '</tr>\n'
    head += '</table>\n'

    open_file_html_new.write(head)

    for line in open_file_html:
        line = line.replace("&gt;", ">")
        line = line.replace("&lt;", "<")
        line = line.replace("&amp;", "&")
        line = line.replace('&quot;', '"')
        line = line.replace('&#x27;',"'")
        line = line.replace('"<','')
        line = line.replace('\\r\\n','<br />')
        line = line.replace('\\n','<br />')
        line = line.replace('</td>','</td>\n')
        line = line.replace('</table>','</table>\n')
        
        open_file_html_new.write(line)

    foot = "\n</body>\n</html>"    
    open_file_html_new.write(foot)

    open_file_html.close()
    open_file_html_new .close()

if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Rekonesans MM wersja 0.1', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str, help='Podaj sciezke do pliku z adresami')
    #parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # rozpoczecie
    start_script = f_czas()

    # odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_nmap_msfconsole = '/home/nano/test1'
    else:
        path_plik_nmap_msfconsole = args.fin
    
    if(os.path.isfile(path_plik_nmap_msfconsole)):
        '''sprawdza czy plik istnieje'''
        path_plik_logu = path_plik_nmap_msfconsole + ".log"
        path_plik_json = path_plik_nmap_msfconsole + ".json"
        path_plik_html = path_plik_nmap_msfconsole + ".html"

        # wywolujemy funkcj, ktora odczyta nam plik linijka po linijce
        f_odczyt_pliku_nmap(path_plik_nmap_msfconsole)
    else:
        print("Plik z danymi nie istnieje!" + path_plik_nmap_msfconsole)
