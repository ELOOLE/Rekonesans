import os
import random
import subprocess
import datetime
import ssl
import urllib.request
import time
import re
import socket
from bs4 import BeautifulSoup, SoupStrainer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException

from urllib.parse import urlparse
from PIL import Image, ImageFont, ImageDraw

import requests
requests.packages.urllib3.disable_warnings()

from impacket.dcerpc.v5 import transport
from impacket.dcerpc.v5.ndr import NULL
from impacket.dcerpc.v5.rpcrt import RPC_C_AUTHN_LEVEL_NONE
from impacket.dcerpc.v5.dcomrt import IObjectExporter


def f_timed(function):
    def wrapper(*args, **kwargs):
        before = time.time()
        results = function(*args, **kwargs)
        after = time.time()
        fname = function.__name__
        
        log = str(datetime.datetime.now())[:19], fname , str(args), results, after-before
        
        for info in log:
            #info = str(info).strip()
            print(f"{info} |", end='')
        print("")
        return results, log
    return wrapper


def f_make_index(data_file, results_path):
    # How many services we will check
    line_count = f_policz_wiersze_w_pliku(data_file)
    #print(f"[i] {line_count} sum of all rows in file")

    # open file with data   
    handler_data_file = open(data_file, 'r')
    l_addr =  []
    # counter of services
    i = 1

    with open(f"{results_path}/index.html", 'w') as result_file:
        result_file.write("<table>\n")

    # read from file line by line
    for service_info in handler_data_file:
        ip = service_info.replace("\"","").lower().strip().split(',')
              
        if extract_ip_addresses(ip[0]) is None:
            line_count -= 1
            print(f"[-] adres ip: [{ip[0]}] niepoprawny")
        else:
            l_addr.append(ip[0])

    l_addr = dict.fromkeys(l_addr)

    for item in l_addr:
        #print(f"[*] Looking for {item} ...")
        
        line_count = len(l_addr)
        #print(f"[*] Progress... {(i*100)/line_count}%")
        with open(f"{results_path}/index.html", 'a') as result_file:
            result_file.write("<tr>\n")
            result_file.write(f"<td>{i}/{line_count}</td>\n")

            if(os.path.isfile(results_path+"/"+item+".html")):
                result_file.write(f'<td><a href="{results_path}/{item}.html">{results_path}/{item}.html</a></td>\n')
                result_file.write(f'<td>')
                file = f"{results_path}/{item}.html"
                size = os.stat(file).st_size
                #size = os.path.getctime(file)
                result_file.write(human_readable_size(size))
                result_file.write(f'</td>\n')
            else:
                result_file.write(f'<td>brak wyniku</td>\n')
                result_file.write(f'<td>&nbsp;</td>\n')
            
            result_file.write("</tr>\n")
        
        i+=1

    with open(f"{results_path}/index.html", 'a') as result_file:
        result_file.write("</table>\n")

    return


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


def human_readable_size(bytes, units=[' bytes','KB','MB','GB','TB', 'PB', 'EB']):
    """ Returns a human readable string representation of bytes """
    return str(bytes) + units[0] if bytes < 1024 else human_readable_size(bytes>>10, units[1:])


def extract_ip_addresses(line):
    ip_regex = r"(?:\d{1,3}\.){3}\d{1,3}"
    return re.match(ip_regex, line)


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

def f_raport_img():
    return '<img src="data:image/png;base64,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"></img>'

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
    elif(typ == "erro"):
        print(style.RED(komunikat))
    elif(typ == "subp"):
        print(style.GREEN(komunikat))    

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


class style():
    BLACK = lambda x: '\033[30m' + str(x)
    RED = lambda x: '\033[31m' + str(x)
    GREEN = lambda x: '\033[32m' + str(x)
    YELLOW = lambda x: '\033[33m' + str(x)
    BLUE = lambda x: '\033[34m' + str(x)
    MAGENTA = lambda x: '\033[35m' + str(x)
    CYAN = lambda x: '\033[36m' + str(x)
    WHITE = lambda x: '\033[37m' + str(x)
    UNDERLINE = lambda x: '\033[4m' + str(x)
    RESET = lambda x: '\033[0m' + str(x)
    

def f_socat(proto, ip, port):
    """ 
    function: f_socat

    @param proto: Proto TCP or UDP
    @param ip: ip address
    @param port: port numer of the service, numerical between 1-65535
    @return: cmd and output of this command or error message
    """
    proto = str(proto).upper()
    if(proto == "TCP"):
        cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {proto}:{ip}:{port},connect-timeout=5 - "
    elif(proto == "UDP"):
        cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {proto}:{ip}:{port},connect-timeout=5 - "
    else:
        return cmd, f"Bad protocol: {proto}"

    # wykonanie polecenia:
    socat_output = f_polecenie_uniwersalne(cmd)

    # sprawdzam
    # [0] - wynik
    # [1] - komunikat bledu
    if(socat_output[1] == None):
        # wynik
        output = f_trim_output(socat_output[0])
        if(len(output) > 0):
            return cmd, output
        else:
            return cmd, "none"
    else:
        return cmd, socat_output[1]    
    

def f_amap(proto, ip, port):
    """ 
    function: f_amap 

    @param proto: Proto TCP or UDP
    @param ip: ip address
    @param port: port numer of the service, numerical between 1-65535
    @return: cmd and output of this command or error message
    """
    proto = str(proto).upper()
    if(proto == "TCP"):
        cmd = f"amap -bqv {ip} {port}"
    elif(proto == "UDP"):
        cmd = f"amap -bqv {ip} {port} -u"
    else:
        return cmd, f"Bad protocol: {proto}"
    
    # wykonanie polecenia
    amap_output = f_polecenie_uniwersalne(cmd)

    # sprawdzam
    # [0] - wynik
    # [1] - komunikat bledu
    if(amap_output[1] == None):
        # wynik
        output = f_trim_output(amap_output[0])
        if(len(output) > 0):
             return cmd, output
        else:
            return cmd, "none"
    else:
        return cmd, amap_output[1]
    

@f_timed
def f_http_code(proto: str, ip: str, port: int, CURL_MAX_TIME: int):
    """ 
    function: f_http_code

    @param proto: Proto TCP or UDP
    @param ip: ip address
    @param port: port numer of the service, numerical between 1-65535
    @CURL_MAX_TIME: int, value of max time for whole curl operation recomended between 1-30
    @return: http_code from server
    """
    
    if(proto.lower() == "tcp"):
        UA = {'User-Agent' :random_ua()}
        lista_protokol = ["http", "https"]
        for h_prot in lista_protokol:
            # adres
            adres = f"{h_prot}://{ip}:{port}"

            response = []

            try:
                # Making a get request
                response = requests.get(adres, verify=False, headers=UA, timeout=CURL_MAX_TIME, allow_redirects=True)
            except Exception as e:
                return adres, str(e)

            return adres, response.status_code
        


def get_tcp_banner(ip, port):
    try:
        port = int(port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)  # Set a timeout for the connection
        s.connect((ip, port))
        banner = s.recv(1024).decode('utf-8')
        s.close()
        return banner
    except Exception as e:
        return f"Error: {str(e)}"


def get_udp_banner(ip, port):
    try:
        port = int(port)
        socket.setdefaulttimeout(5)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01', (ip, port))
        response, _ = s.recvfrom(1024)
        return response
    except:
        return None


def save_results_in_file(content, ip, port,protokol,usluga, opis_nmap, results_path, action):
    with open(f"{results_path}/{ip}.html", 'a') as result_file:
        result_file.write(f"[*] Service {ip} on port {port} / {protokol}, {usluga}, {opis_nmap} <br/>")
        if(len(str(content))> 0 ):
            result_file.write(f"[*] {datetime.datetime.now()} <br/>")
            result_file.write(f"[*] Results of {action}:<br/>")
            result_file.write(str(content)+"<br/>")
            result_file.write("---<br/>")
            result_file.write("<br/>")


def print_result(conten, ip, port,severity):
    if(severity == 0):
        msg = f"[*] ip:{ip}:{port} {conten}"
    elif(severity == 1):
        msg = f"[+] ip:{ip}:{port} {conten}"
    elif(severity == 2):
        msg = f"[-] ip:{ip}:{port} {conten}"
    return print(msg)