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

# dane do zrzutu danych
data = {}

#banner aplikacji
baner = pyfiglet.figlet_format("Rekonesans")
print(baner)

def f_odczyt_pliku_nmap(plik):
    print(f"{f_czas()} | odczytuje plik z danymi: {plik}")
    otwarty_plik_nmap = open(plik, 'r')

    # licze ile jest lini w pliku z danymi
    line_count = 0
    for line in otwarty_plik_nmap:
        if line != "\n":
            line_count += 1
    otwarty_plik_nmap.close()
    print(f"Ilosc zadan do wykonania: {line_count} \n")

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

        print(f"({i}/{line_count}) | {f_czas()} | IP: {ip} proto:{protokol} port:{port} usluga: {usluga}")
        i+=1

        r = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        if r.match(ip) is None:
            print(f"{f_czas()} | Wpis nie zawiera poprawnego adresu IP [{ip}]")
        else:
            # pierwsza funkcja socat na określenie hosta
            output_socat = f_socat(ip,port,protokol)

            # curl - odpytuje host i daje info dla wykonania screen shota 
            output_curl = f_curl(ip,port,protokol)

            # screen shot w przypadku kiedy curl zwroci 200, 302, 404
            output_screen_shot_web = "---"
            if(" 200 " in str(output_curl) or " 302 " in str(output_curl) or " 404 " in str(output_curl)):
                output_screen_shot_web = f_screen_shot_web(ip,port,protokol)

            # zapis do pliku *.json
            data['host'].append({'ip':f'{ip}','port':f'{port}','protokol':f'{protokol}','usluga':f'{usluga}','opis':f'{opis_nmap}','socat':f'{output_socat}','curl':f'{output_curl}','screen_shot':f'{output_screen_shot_web}'})
        
    with open('/home/nano/data.json', 'w') as outfile:
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

def f_socat(ip,port,protokol):
    protokol = str.upper(protokol)
    cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol}:{ip}:{port},connect-timeout=2 - "
    ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ps.communicate()[0]

    return output

def f_curl(ip,port,protokol):
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

def f_dirb(ip,port,h_proto):
    czas = datetime.datetime.now()
    cmd = f"dirb {h_proto}://{ip}:{port} /usr/share/wordlists/dirb/common.txt -f -S" 
    cmd_p = f"{czas} | {cmd}"
    print (cmd_p)
    
    dirb = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = dirb.communicate()[0]

    return output
        
def f_screen_shot_web (ip,port,protokol):
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

def f_czas ():
    return datetime.datetime.now()

def f_get_links_from_web(ip,port,protokol):
    czas = datetime.datetime.now()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Rekonesans MM wersja 0.1', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str, help='Podaj sciezke do pliku z adresami')
    parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # odczytujemy plik z metasploit
    # services -u -c proto,port,name -o /home/user/Pobrane/dane.txt
    # services -u -c port,proto,name,info - o /home/user/rand1234
    # odczyt pliku

    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_nmap_msfconsole = '/home/nano/test1'
    else:
        path_plik_nmap_msfconsole = args.fin
    
    # wywołujemy funkcję, która odczyta nam plik linijka po linijce
    f_odczyt_pliku_nmap(path_plik_nmap_msfconsole)
