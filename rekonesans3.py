###############################################################################
# rekonesans v0.2
# Written by MM
# Copyright 2021
## input: metasploit(db_nmap - discover)
# services -u -c port,proto,name,info -o /home/user/rand1234
###############################################################################

import os
import socket
import shlex
import subprocess
import signal
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
from selenium.common.exceptions import TimeoutException

from bs4 import BeautifulSoup, SoupStrainer

from random import randrange

from PIL import Image, ImageFont, ImageDraw

import sys
import getopt
from impacket.dcerpc.v5 import transport
from impacket.dcerpc.v5.ndr import NULL
from impacket.dcerpc.v5.rpcrt import RPC_C_AUTHN_LEVEL_NONE
from impacket.dcerpc.v5.dcomrt import IObjectExporter

# dane do zrzutu danych zwiazane wlasnie z plikiem *.json
ilosc_uslug = 0

baner = pyfiglet.figlet_format("Rekonesans")
print(baner)


def f_odczyt_pliku_nmap(plik):
    f_zapis_log(
        "f_odczyt_pliku_nmap",
        "info",
        f"odczytuje plik z danymi: {plik}")

    # ilosc odczytanych wierszy w pliku zrodlowym
    line_count = f_policz_wiersze_w_pliku(plik)
    f_zapis_log(
        "f_odczyt_pliku_nmap",
        "info",
        f"Ilosc zadan do wykonania: {line_count}")
    global ilosc_uslug
    ilosc_uslug = line_count

    # otwieram ponownie
    otwarty_plik_nmap = open(plik, 'r')
    i = 1
    data = {}
    data['skan'] = []

    # czytamy linijka po linijce
    for linijka in otwarty_plik_nmap:
        # rozpoczynamy parsowanie pliku
        # wiersz jest oddzielany poprzez "," (przecinek)
        wynik = linijka.split(',')
        ip = wynik[0].replace("\"", "").rstrip("")
        port = wynik[1].replace("\"", "").rstrip("")
        protokol = wynik[2].replace("\"", "").rstrip("")
        usluga = wynik[3].replace("\"", "").rstrip("")
        opis_nmap = wynik[4].replace("\"", "").rstrip("")

        f_zapis_log(
            "---------",
            "-------------------",
            "-----------------------------------------------------------------")
        
        f_zapis_log(
            "f_odczyt_pliku_nmap",
            "info   ",
            f"({i}/{line_count}) | proto:{protokol} IP:{ip} port:{port} usluga:{usluga}")

        f_zapis_log(
            "---------",
            "-------------------",
            "-----------------------------------------------------------------")

        r = re.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}")
        if r.match(ip) is None:
            f_zapis_log(
                "f_odczyt_pliku_nmap",
                "info",
                f"Wpis nie zawiera poprawnego adresu IP [{ip}]")
            ilosc_uslug -= 1
        else:
            # zapis do pliku *.json
            tmp_dict = {ip: {
                'ip': ip,
                'port': port,
                'protokol': protokol,
                'usluga': usluga,
                'opis': opis_nmap
            }}

            ######################################################
            # socat
            ######################################################
            cmd = f"echo -ne \\x01\\x00\\x00\\x00 | socat -t 1 {protokol.upper()}:{ip}:{port},connect-timeout=5 - "
            socat_output = f_polecenie_uniwersalne("socat", cmd)
            if(socat_output[1] == None):
                output = f_trim_output(socat_output[0])
                if(len(output) > 0):
                    tmp_dict[ip]['socat'] = f'{output}\n'

            ######################################################
            # cURL, links, web_shot
            ######################################################
            if(protokol.lower() == "tcp"):
                lista_protokol = ["http", "https"]
                for h_prot in lista_protokol:
                    # adres
                    adres = f"{h_prot}://{ip}:{port}"
                    cmd = "curl -k -I -s -o /dev/null -w \"%{http_code}\" " + adres
                    curl_output = f_polecenie_uniwersalne("curl", cmd)

                    http_code = "000"
                    if(curl_output[1] == None):
                        http_code = curl_output[0].decode('utf-8')
                        if(http_code != "000"):
                            tmp_dict[ip][f'curl:{h_prot}:http_code'] = f'{http_code}\n'

                    # links, screenshots
                    lista_http_code = ['200','301','302','404']
                    if(http_code in lista_http_code):
                        # info 
                        cmd = f"curl -I -k -s {h_prot}://{ip}:{port} --max-time 3 --no-keepalive"
                        curl_output = f_polecenie_uniwersalne("curl", cmd)
                        if(curl_output[1] == None):
                            output = f_trim_output(curl_output[0])
                            tmp_dict[ip][f'curl:{h_prot}:info'] = f'{output}\n'

                        try:
                            # scrrenshot
                            output_screen_shot_web = f_screen_shot_web(adres)
                            if(output_screen_shot_web == "error"):
                                tmp_dict[ip][f'web_shot'] = f'{output_screen_shot_web}\n'
                            else:
                                tmp_dict[ip][f'web_shot'] = f'<img src="{output_screen_shot_web}">\n'

                            # zbierz linki ze strony
                            if(http_code == "200"):
                                output_links_from_web = f_get_links_from_web(adres)
                                tmp_dict[ip][f'links:{h_prot}'] = f'{output_links_from_web}\n'

                            # przekierowanie
                            if(http_code == "301" or http_code == "302"):
                                redirect_url = ""
                                cmd = "curl -k -I -s -o /dev/null -w \"%{redirect_url}\" " + adres
                                curl_output = f_polecenie_uniwersalne("curl", cmd)
                                if(curl_output[1] == None):
                                    redirect_url = curl_output[0].decode('utf-8')
                                    tmp_dict[ip][f'curl:{h_prot}:redirect_url:addr'] = f'{redirect_url}\n'

                                    cmd = "curl -k -I -s -o /dev/null -w \"%{http_code}\" " + redirect_url
                                    curl_output = f_polecenie_uniwersalne("curl", cmd)
                                    
                                    http_code = "000"
                                    if(curl_output[1] == None):
                                        http_code = curl_output[0].decode('utf-8')
                                        tmp_dict[ip][f'curl:{h_prot}:redirect_url:http_code'] = f'{http_code}\n'

                                        if(http_code == "200" or http_code== "404"):
                                            # screenshot
                                            output_screen_shot_web = f_screen_shot_web(redirect_url)
                                            if(output_screen_shot_web == "error"):
                                                tmp_dict[ip][f'web_shot:redirect_url'] = f'{output_screen_shot_web}\n'
                                            else:
                                                tmp_dict[ip][f'web_shot:redirect_url'] = f'<img src="{output_screen_shot_web}">\n'

                                        if(http_code == "200"):
                                            # linki
                                            output_links_from_web = f_get_links_from_web(redirect_url)
                                            tmp_dict[ip][f'links:{h_prot}:redirect_url'] = f'{output_links_from_web}\n'

                        except Exception as er:
                            f_zapis_log(
                                "f_odczyt_pliku_nmap/f_screen_shot_web",
                                "error",
                                f"Wyjatek scr shot {h_prot}://{ip}:{port} {str(er)}")
                            output_screen_shot_web = "none"

                        # zapis do pliku *.json
                        tmp_dict[ip]['wskazowka:nikto'] = f'nikto -h {ip}\n'
                        tmp_dict[ip]['wskazowka:dirb'] = f'dirb {h_prot}://{ip} /usr/share/wordlists/dirb/common.txt\n'
                        tmp_dict[ip]['wskazowka:crawl:wget'] = f'wget --wait=2 --level=inf --limit-rate=20K --recursive --page-requisites --user-agent=Mozilla --no-parent --convert-links --adjust-extension --no-clobber -e robots=off {h_prot}://{ip}:{port} --no-check-certificate'
            #
            # http://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
            #
            # ports / services

            # 7 Echo
            # 19 Chargen
            # 20-21 FTP
            if(port == "20" or port == "21" or "ftp" in opis_nmap.lower()):
                # zapis do pliku *.json
                tmp_dict[ip]['wskazowka:[NSE]:nmap'] = f'nmap --script ftp* -p{port} -d {ip} -Pn -n\n'
                tmp_dict[ip]['wskazowka:[Brute-force]:hydra'] = f'hydra -s {port} -C /usr/share/wordlists/ftp-default-userpass.txt -u -f {ip} ftp\n'
                tmp_dict[ip]['wskazowka:[Brute-force]:patator'] = f"patator ftp_login host={ip} user=FILE0 0=logins.txt password=asdf -x ignore:mesg='Login incorrect.' -x ignore,reset,retry:code=500"

            # port 22 - Encrypted
            #output_ssh_mechanizm = "none"
            if(port == "22" or "ssh" in opis_nmap.lower()):
                cmd = f'nmap --script "ssh* and not ssh-brute and not ssh-run" -p22 -Pn -n {ip}'
                ssh_output = f_polecenie_uniwersalne("ssh", cmd)

                if(ssh_output[1] == None):
                    output = f_trim_output(ssh_output[0])
                    tmp_dict[ip]['ssh'] = f'{output}\n'

                tmp_dict[ip]['wskazowka:[NSE]:nmap'] = f'nmap --script ssh-brute -d {ip}'
                tmp_dict[ip]['wskazowka:[Brute-force]:patator'] = f"patator ssh_login host={ip} user=FILE0 0=logins.txt password=$(perl -e ""print 'A'x50000"") --max-retries 0 --timeout 10 -x ignore:time=0-3"
                tmp_dict[ip]['wskazowka:[Brute-force]:info'] = f"Brute-force uslugi ssh z powodu ograniczen ilosciowych zapytan, zaleca sie uzyc malego slownika"

            # port 23 telnet
            if(port == "23" or "telnet" in opis_nmap.lower()):
                tmp_dict[ip]['wskazowka:[NSE]:nmap'] = f"nmap --script telnet* -p23 -d {ip}"

            # port 25 smtp
            # output_smtp = "none"
            if(port == "25" or "smtp" in opis_nmap.lower()):
                cmd = f'nmap --script smtp* -p25 {ip} -Pn -n'
                smtp_output = f_polecenie_uniwersalne("smtp", cmd)

                if(smtp_output[1] == None):
                    output = f_trim_output(smtp_output[0])
                    tmp_dict[ip]['smtp'] = f'{output}\n'

                tmp_dict[ip]['wskazowka:enum1'] = f"smtp-user-enum -M VRFY -U users.txt -t {ip}"
                tmp_dict[ip]['wskazowka:enum2'] = f"smtp-user-enum -M EXPN -u admin1 -t {ip}"
                tmp_dict[ip]['wskazowka:enum3'] = f"smtp-user-enum.pl -M RCPT -U users.txt -T mail-server-ips.txt {ip}"
                tmp_dict[ip]['wskazowka:enum4'] = f"smtp-user-enum.pl -M EXPN -D example.com -U users.txt -t {ip}"

            # 42 WINS Replication
            # 43 WHOIS
            # 49 TACACS

            # port 53, dns
            if(port == "53"):
                cmd = f'dig ANY @{ip}'
                dig_output = f_polecenie_uniwersalne("dig", cmd)

                if(dig_output[1] == None):
                    output = f_trim_output(dig_output[0])
                    tmp_dict[ip]['dns:dig'] = f'{output}\n'

                tmp_dict[ip]['wskazowka:dnsrecon'] = f"dnsrecon -a -w -d JAKAS.DOMENA.pl -n {ip} --csv /home/user/dnsrecon{ip}.csv</b> do zapisu, musi byc podana sciezna bezwzgledna inaczej nie zapisze"
                tmp_dict[ip]['wskazowka:dnsenum'] = f"dnsenum --noreverse {ip}"

            # port 67, 68, DHCP protocol: UDP
            # 69 TFTP
            # 70 Gopher
            # 79 Finger
            # 80 HTTP
            # 88 Kerberos
            # 102 MS Exchange
            # 110 pop3
            # 113 Ident
            # 119 NNTP (Usenet)
            # port 123, NTP, protocol: UDP

            # port 135
            #output_dcerpc_p135 = "none"
            if(port == "135"):
                output_dcerpc_p135 = f_rpc_p135(ip)
                tmp_dict[ip]['dcerpc'] = f'{output_dcerpc_p135}'

            # port 137 - 139 NetBIOS
            #output_enum4linux = "none"
            if(port == "139"):
                cmd = f"enum4linux {ip}"
                enum4linux_output = f_polecenie_uniwersalne("enum4linux", cmd)

                if(enum4linux_output[1] == None):
                    output = f_trim_output(enum4linux_output[0])
                    tmp_dict[ip]['enum4linux'] = f'{output}\n'

            # port 143 imap
            # port 161-162 snmp
            # 177 XDMCP
            # 179 BGP
            # 201 AppleTalk
            # 264 BGMP
            # 318 TSP
            # 381-383 HP Openview
            # 389 LDAP
            # 411-412 Direct Connect - Peer to Peer
            # 443 HTTP over SSL - Encrypted
            # 445 Microsoft DS
            # 464 Kerberos
            # 465 SMTP over SSL - Encrypted
            # 497 Retrospect
            # 500 udp - ISAKMP - Encrypted
            # port 512
            # port 513
            # port 514
            # 515 LPD/LPR
            # 520 RIP
            # 521 RIPng (IPv6)
            # 540 UUCP
            # 543 klogin, Kerberos login
            # 544 kshell, Kerberos Remote shell
            # 546 DHCPv6 client
            # 547 DHCPv6 server
            # 554 RTSP
            # 560 rmonitor
            # 563 NNTP over SSL - Encrypted
            # 587 SMTP
            # 591 FileMaker
            # 593 Microsoft DCOM
            # 631 Internet Printing
            # 636 LDAP over SSL - Encrypted
            # 639 MSDP (PIM)
            # 646 LDP (MPLS)
            # 691 MS Exchange
            # 860 iSCSI
            # 873 rsync
            # 902 VMware Server
            # 989-990 FTP over SSL - Encrypted
            # 993 IMAP4 over SSL - Encrypted
            # 995 POP3 over SSL - Encrypted
            # 1025 Microsoft RPC
            # 1026-1029 Windows Messenger
            # 1080 SOCKS Proxy
            # 1080 MyDoom - Malicious
            # 1194 OpenVPN
            # 1214 Kazaa - Peer to Peer
            # 1241 Nessus
            # 1311 Dell OpenManage
            # 1337 WASTE - Peer to Peer
            # 1433-1434 Microsoft SQL
            # 1512 WINS
            # 1589 Cisco VQP
            # 1701 L2TP
            # 1723 MS PPTP
            # 1725 Steam - Gaming
            # 1741 CiscoWorks 2000
            # 1755 MS Media Server - Streaming
            # 1812-1813 RADIUS
            # 1863 MSN - Chat
            # 1985 Cisco HSRP
            # 2000 Cisco SCCP
            # 2002 Cisco ACS
            # 2049 NFS
            # 2082-2083 cPanel
            # 2100 Oracle XDB
            # 2222 DirectAdmin
            # 2302 Halo - Gaming
            # 2483-2484 Oracle DB
            # 2745 Bagle.H - Malicious
            # 2967 Symantec AV
            # 3050 Interbase DB
            # 3074 XBOX Live - Gaming
            # 3124 HTTP Proxy
            # 3127 MyDoom - Malicious
            # 3128 HTTP Proxy
            # 3222 GLBP
            # 3260 iSCSI Target
            # 3306 MySQL
            # 3389 Terminal Server
            # 3689 iTunes
            # 3690 Subversion
            # 3724 World of Warcraft - Gaming
            # 3784-3785 Ventrilo - Streaming
            # 4333 mSQL
            # 4444 Blaster - Malicious
            # 4664 Google Desktop
            # 4672 eMule - Peer to Peer
            # 4899 Radmin
            # 5000 UPnP
            # 5001 Slingbox - Streaming
            # 5001 iperf
            # 5004-5005 RTP - Streaming
            # 5050 Yahoo! Messenger - Chat
            # 5060 SIP
            # 5190 AIM/ICQ - Chat
            # 5222-5223 XMPP/Jabber - Chat
            # 5432 PostgreSQL
            # 5500 VNC Server
            # 5554 Sasser - Malicious
            # 5631-5632 pcAnywhere
            # 5800 VNC over HTTP
            # 5900+ VNC Server
            # 6000-6001 X11
            # 6112 Battle.net - Gaming
            # 6129 DameWare
            # 6257 WinMX - Peer to Peer
            # 6346-6347 Gnutella - Peer to Peer
            # 6443 kubernetes

            if(port == "6443"):
                cmd = f"curl -sk https://{ip}:{port}/version "
                kubernetes_output = f_polecenie_uniwersalne("curl", cmd)

                if(kubernetes_output[1] == None):
                    output = f_trim_output(kubernetes_output[0])
                    tmp_dict[ip]['curl:kebernetes'] = f'{output}\n'
            
            # 6500 GameSpy Arcade - Gaming
            # 6566 SANE
            # 6588 AnalogX
            # 6665-6669 IRC - Chat
            # 6679/6697 IRC over SSL - Chat
            # 6699 Napster - Peer to Peer
            # 6881-6999 BitTorrent - Peer to Peer
            # 6891-6901 Windows Live - Chat
            # 6970 Quicktime - Streaming
            # 7212 GhostSurf
            # 7648-7649 CU-SeeMe - Chat
            # 8000 Internet Radio - Streaming
            # 8080 HTTP Proxy
            # 8086-8087 Kaspersky AV
            # 8118 Privoxy
            # 8200 VMware Server
            # 8500 Adobe ColdFusion
            # 8767 TeamSpeak - Chat
            # 8866 Bagle.B - Malicious
            # 9100 HP JetDirect
            # 9101-9103 Bacula
            # 9119 MXit - Chat
            # 9800 WebDAV
            # 9898 Dabber - Malicious
            # 9988 Rbot/Spybot - Malicious
            # 9999 Urchin
            # 10000 Webmin
            # 10000 BackupExec
            # 10113-10116 NetIQ
            # 11371 OpenPGP
            # 12035-12036 Second Life - Gaming
            # 12345 NetBus - Malicious
            # 13720-13721 NetBackup
            # 14567 Battlefield - Gaming
            # 15118 Dipnet/Oddbob - Gaming
            # 19226 AdminSecure
            # 19638 Ensim
            # 20000 Usermin
            # 24800 Synergy - Streaming
            # 25999 Xfire - Chat
            # 27015 Half-Life - Gaming
            # 27374 Sub7 - Malicious
            # 28960 Call of Duty - Gaming
            # 31337 Back Orifice - Malicious
            # 33434+ traceroute
            i += 1
            data['skan'].append(tmp_dict)
    ###########################################################################
    # with open(path_plik_json, 'a+') as outfile:
    #    json.dump(data, outfile)

    # zapisuje dane do pliku *.json
    wynik = f_zapisz_dane_jako_json(data, path_plik_json)
    typ_komunikatu = ""
    if(wynik == "sukces"):
        typ_komunikatu = "info"
    else:
        typ_komunikatu = "error"
    f_zapis_log("wynik: f_zapisz_dane_jako_json", typ_komunikatu, wynik)

    # zapisuje dane do pliku *.html
    f_parsuj_plik_json_na_html(path_plik_json, path_plik_html)

    # try:
    #    raport_html = open(path_plik_html, 'w')
    #    raport_html.write(json2html.convert(json = data, table_attributes='width="100%"', clubbing=True, encode=False, escape=True))
    #    raport_html.close()
    #    f_html_parser(path_plik_html)
    # except Exception as e:
    #    f_zapis_log("f_odczyt_pliku_nmap-raport_html",e,"error")

    otwarty_plik_nmap.close()

#####################################################################################################################


def f_polecenie_uniwersalne(polecenie, cmd):
    '''SOCAT
    INPUT:
        cmd - command
    OUTPUT:
        wynik polecenia
    '''     
    
    # zapisuje do logu wykonane polecenie
    f_zapis_log(f"{polecenie}", "info   ", cmd)
    ps = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)

    try:
        output, errs = ps.communicate(timeout=20)
        #output = f_trim_output(output) 
            
        # zapisuje do logu wynik polecenia
        f_zapis_log(f"{polecenie}", "results", output)
        return output, errs
    except subprocess.TimeoutExpired:
        ps.kill()
        # zapisuje do logu informacje o bledzie
        f_zapis_log(f"{polecenie}", "error  ", "TimeoutExpired")
        return "", "TimeoutExpired"
    except Exception as error:
        f_zapis_log(f"{polecenie}", "error  ", error)
        return "", error 


def f_curl_variables_JS(addr):
    # budujemy polecenie
    cmd_curl = f"curl -Lks {addr} | grep window "

    # zapisujemy zbudowane polecenie do pliku logu
    f_zapis_log("f_curl_variables_JS", "info", cmd_curl)

    args1 = shlex.split(cmd_curl)
    ps_cmd_curl1 = subprocess.Popen(
        args1,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    try:
        curl_output = str(ps_cmd_curl1.communicate(timeout=10)[0].decode('utf-8'))

         # zmienna [wynik] ma dane, ktore zostana zwrocone przez funkcje
        output = str(curl_output).strip()
        output_window = output.split("\n")
        link_addr = ""

        for x in output_window:
            if("window" in x):
                link_addr = x

        start = link_addr.find("/")
        end = link_addr[start:].find('"') + start

        output = link_addr[start + 1:end]

        if(len(output) == 0):
            output = "none"

        f_zapis_log("f_curl_variables_JS", "info", output)
    except subprocess.TimeoutExpired:
        ps_cmd_curl1.kill()
        output = "TimeoutExpired"
        # zapisujemy do logu co zwrocila [f_curl]
        f_zapis_log("f_curl_variables_JS", "error", output)

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


def f_screen_shot_web(adres):
    '''SCREEN SHOT of WEB PAGE '''
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.headless = True
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)

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
        f_zapis_log("f_screen_shot_web", "info", URL)

        driver.get(URL)
        def S(X): return driver.execute_script(
            'return document.body.parentNode.scroll' + X)
        # driver.set_window_size(1200,S('Height'))

        driver.set_window_size(S('Width'), S('Height'))
        # driver.set_window_size(1200,1200)

        # nazwa pliku *.png
        nazwa_pliku = path_plik_nmap_msfconsole + \
            "_" + f"{ip}_{port}_{protokol}.png"
        f_zapis_log(
            "f_screen_shot_web",
            "info",
            f"nazwa pliku screen shot-a {nazwa_pliku}")

        # tresc znaku wodnego nanoszonego na *.png
        znak_wodny = f"{f_czas()} | Protokol: [{protokol}], adres ip: [{ip}], port: [{port}]"
        f_zapis_log("f_screen_shot_web", "info", f"znak wodny {znak_wodny}")

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
        f_zapis_log(
            "f_screen_shot_web",
            "info",
            f"Naniesiono podpis na obrazek: {nazwa_pliku}")

        # convert png to jpg
        nazwa_pliku_jpg = nazwa_pliku[:-3] + "jpg"
        img_to_jpg = podpisz_screena.convert('RGB')
        img_to_jpg.save(nazwa_pliku_jpg)
        f_zapis_log(
            "f_screen_shot_web",
            "info",
            f"konversja {nazwa_pliku} -> {nazwa_pliku_jpg}")

        # skasowac png
        os.remove(nazwa_pliku)
        f_zapis_log(
            "f_screen_shot_web",
            "info",
            f"skanowano plik {nazwa_pliku}")
        obrazek = os.path.basename(nazwa_pliku_jpg)
    except Exception as error:
        f_zapis_log("f_screen_shot_web", "error", error)
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

    #NetworkAddr = bindings[0]['aNetworkAddr']
    for binding in bindings:
        NetworkAddr = binding['aNetworkAddr']
        #print ("Address: " + NetworkAddr)
        adresy_ip += NetworkAddr + "\n"

    wynik += adresy_ip

    f_zapis_log(
        "f_rpc_p135",
        "info",
        wynik)
   
    #f_zapis_log("f_rpc_p135", "info", adresy_ip)
    
    return wynik


def f_czas():
    '''Zwraca w wyniku aktualny czas'''
    return datetime.datetime.now()


def f_zapis_log(zrodlo, typ, dane):
    '''Zapis wyniku dzialania do pliku logu'''
    '''Sciezka pliku w zmiennej [path_plik_logu]'''
    # sprawdzam istnienie pliku, je|eli istnieje dopisze w innym przypadku
    # nadpisze '''
    if(os.path.isfile(path_plik_logu)):
        plik_logu = open(path_plik_logu, 'a+')
    else:
        plik_logu = open(path_plik_logu, 'w+')
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
    plik_logu.write(komunikat + '\n')

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

def f_zapisz_dane_jako_json(data, dstfile):
    wynik = ""
    try:
        with open(dstfile, 'a+') as outfile:
            json.dump(data, outfile)
        wynik = "sukces"
    except Exception as e:
        wynik = str(e)

    return wynik


def f_parsuj_dane_json_na_html(data, dstfile):
    wynik = ""
    try:
        raport_html = open(dstfile, 'w')
        raport_html.write(
            json2html.convert(
                json=data,
                table_attributes='width="100%"',
                clubbing=True,
                encode=False,
                escape=True))
        raport_html.close()
        f_html_parser(dstfile)
        wynik = "sukces"
    except Exception as e:
        wynik = str(e)

    return wynik


def f_parsuj_plik_json_na_html(srcfile, dstfile):
    wynik = ""
    try:
        plik_json = open(srcfile, 'r')
        odczyt_pliku = plik_json.read()
        raport_html = open(dstfile, 'w')
        raport_html.write(
            json2html.convert(
                json=odczyt_pliku,
                table_attributes='width="100%"',
                clubbing=True,
                encode=False,
                escape=True))
        raport_html.close()
        f_html_parser(dstfile)
        wynik = "sukces"
    except Exception as e:
        wynik = str(e)

    return wynik


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
        line = line.replace('&#x27;', "'")
        line = line.replace('"<', '')
        line = line.replace('\\r\\n', '<br>')
        line = line.replace('\\n', '<br>')
        line = line.replace('</td>', '</td>\n')
        line = line.replace('</table>', '</table>\n')

        open_file_html_new.write(line)

    foot = "\n</body>\n</html>"
    open_file_html_new.write(foot)

    open_file_html.close()
    open_file_html_new .close()


if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(
        description='Rekonesans MM wersja 0.1',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str,
                        help='Podaj sciezke do pliku z adresami')
    #parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # rozpoczecie
    start_script = f_czas()

    # odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_nmap_msfconsole = '/home/user/ltest1'
    else:
        path_plik_nmap_msfconsole = args.fin

    if(os.path.isfile(path_plik_nmap_msfconsole)):
        '''sprawdza czy plik istnieje'''
        path_plik_logu = path_plik_nmap_msfconsole + ".log"
        path_plik_json = path_plik_nmap_msfconsole + ".json"
        path_plik_html = path_plik_nmap_msfconsole + ".html"

        # wywolujemy funkcje, ktora odczyta nam plik linijka po linijce
        f_odczyt_pliku_nmap(path_plik_nmap_msfconsole)
    else:
        print("Plik z danymi nie istnieje!" + path_plik_nmap_msfconsole)
