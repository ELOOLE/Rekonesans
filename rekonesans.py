###############################################################################
# rekonesans v0.2
# Written by MM
# Copyright 2021
#---
# nmap -sV -A -O -p- XcelX -oA PlikWynikowy
#---
# services -u -O 1 -c  port,proto,name,info -o /home/user/targets_ports - sort by host
# services -u -O 2 -c  port,proto,name,info -o /home/user/targets_ports - sort by port
###############################################################################
from multiprocessing.pool import ThreadPool
import os
import argparse
from pickle import FALSE
import sys
from tkinter.ttk import Style
import re
from xmlrpc.client import boolean
import f_biblioteka, f_json


# Global variables
LINE_COUNT = 0


# auxiliary funciton to make it work
def map_helper(args):
    return f_odczyt_pliku_nmap(*args)


def f_odczyt_pliku_nmap(plik):
    # How many services we will check
    LINE_COUNT = f_biblioteka.f_policz_wiersze_w_pliku(plik)

    # open file with data   
    handler_file_with_data = open(plik, 'r')
    
    # Results set
    data = {}
    data['skan'] = []

    # counter of services
    i = 1

    # read from file line by line
    for service_info in handler_file_with_data:
        # array with addr and detailes of services
        TResults = service_info.split(',')
        
        # variables about service information 
        ip = TResults[0].replace("\"", "").strip("")
        port = TResults[1].replace("\"", "").strip("")
        protokol = TResults[2].replace("\"", "").strip("")
        usluga = TResults[3].replace("\"", "").strip("")
        opis_nmap = TResults[4].replace("\"", "").strip("")
       
        # check if ip is real ip value
        r = re.compile("\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}")

        #r = re.compile("^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")
        if r.match(ip) is None:
            f_biblioteka.f_zapis_log(
                "read from file",
                "warn",
                f"Entry don't have correct IP addr [{ip}]. The wrong address will be skipped.",
                pathLogFile=path_plik_logu)
            
            #print(f"wynik: {r.match(ip)}, {r2.match(ip)}")

            LINE_COUNT -= 1
        else:
            f_biblioteka.f_zapis_log(
                "f_odczyt_pliku_nmap",
                "info",
                f"({i}/{LINE_COUNT}) | proto:{protokol} IP:{ip} port:{port} usluga:{usluga}",
                pathLogFile=path_plik_logu)

            # zapis do pliku *.json
            tmp_dict = {ip: {
                'ip': ip,
                'port': port,
                'protokol': protokol,
                'usluga': usluga,
                'opis': opis_nmap,
            }}

            # socat
            socat_output = f_biblioteka.f_socat(protokol, ip, port)
            socat = {}
            socat['Start'] = str(socat_output[1][0])
            socat['Duration(sec.)'] = str(socat_output[1][4])
            socat['Sended_command'] = str(socat_output[0][0])
            socat['Results'] = str(socat_output[0][1])
            tmp_dict[ip]['socat'] = socat
            
            # amap
            amap_output = f_biblioteka.f_amap(protokol, ip, port)
            amap = {}
            amap['Start'] = str(amap_output[1][0])
            amap['Duration(sec.)'] = str(amap_output[1][4])
            amap['Sended_command'] = str(amap_output[0][0])
            amap['Results'] = str(amap_output[0][1])
            tmp_dict[ip]['amap'] = amap

            # http_code
            http_code_output = f_biblioteka.f_http_code(protokol, ip, port, CURL_MAX_TIME)
            tmp_dict[ip]['http_code'] = f'Start work at: {str(http_code_output[1][0])}\n',f'{str(http_code_output[1][4])}\n',f'Sended command: {str(http_code_output[0][0])}','Results: ',[f'{str(http_code_output[0][1])}\n']

            # web page screen shot
            lista_http_code = ['200','204','301','302','307','401','403','404','405','500']
            if(str(http_code_output[1][3][1]) in lista_http_code):
                f_biblioteka.f_zapis_log("web_page_screen_shot","start time",str(f_biblioteka.f_czas()),pathLogFile=path_plik_logu)
                adres = http_code_output[1][3][0]
                try:
                    # screenshot
                    output_screen_shot_web = f_biblioteka.f_screen_shot_web(adres, path_plik_logu)
                    if(output_screen_shot_web == "error"):
                        tmp_dict[ip][f'web_page_screen_shot'] = f'{output_screen_shot_web}\n'
                    else:
                        tmp_dict[ip][f'web_page_screen_shot'] = f'<img src="{output_screen_shot_web}">\n'
                    f_biblioteka.f_zapis_log("web_page_screen_shot","results",str(output_screen_shot_web),pathLogFile=path_plik_logu)
                except Exception as e:
                    f_biblioteka.f_zapis_log("web_page_screen_shot","results",str(e),pathLogFile=path_plik_logu)
                f_biblioteka.f_zapis_log("web_page_screen_shot","end time",str(f_biblioteka.f_czas()),pathLogFile=path_plik_logu)
            else:
                f_biblioteka.f_zapis_log("web_page_screen_shot",str(http_code_output[1]),str(f_biblioteka.f_czas()),pathLogFile=path_plik_logu)
                
            #print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! str(http_code_output[1][3][0]: {str(http_code_output[1][3][0])}")
            # zbierz linki ze strony
            if(str(http_code_output[1][3][1]) == "200"):
                adres = http_code_output[1][3][0]
                output_links_from_web = f_biblioteka.f_get_links_from_web(adres)
                tmp_dict[ip][f'adres'] = f'{adres}\n'
                tmp_dict[ip][f'links'] = f'{output_links_from_web}\n'


            # 20-21 FTP
            # port 20 data transfer
            if(port == "21" or "ftp" in opis_nmap.lower()) and protokol.lower() == "tcp":
                if AGGRESIVE:
                    f_biblioteka.f_zapis_log(
                                    f"port {port}",
                                    "subp",
                                    f"uruchamiam subprocess - nmap bruteforce ftp",
                                    pathLogFile=path_plik_logu)
                    os.system(f"nmap --script ftp* -p{port} {ip} -Pn -n > {FILE_OUTPUT}_nmap_ftp_{ip}_{port}.txt &")
                    tmp_dict[ip]['nmap:raport'] = f'<a href="{FILE_OUTPUT}_nmap_ftp_{ip}_{port}.txt">{f_biblioteka.f_raport_img()}</a><br />---<br />Time: ~10min<br />nmap --script ftp* -p{port} -d {ip} -Pn -n'
                #---
                tmp_dict[ip]['wskazowka:hydra'] = f'hydra -s {port} -L Rekonesans/dictionary/s_user.lst -P Rekonesans/dictionary/s_pass_admin.txt -u -f {ip} ftp\n'
                tmp_dict[ip]['wskazowka:patator'] = f"patator ftp_login host={ip} port={port} user=FILE0 0=Rekonesans/dictionary/s_user.lst password=FILE1 1=Rekonesans/dictionary/s_pass_admin.txt -x ignore:mesg='Login incorrect.' -x ignore,reset,retry:code=500"

            # port 22 - Encrypted
            #output_ssh_mechanizm = "none"
            if(port == "22" or "ssh" in opis_nmap.lower()) and protokol.lower() == "tcp":
                cmd = f'nmap --script "ssh* and not ssh-brute and not ssh-run" -p {port} -Pn -n {ip}'
                ssh_output = f_biblioteka.f_polecenie_uniwersalne(cmd)

                if(ssh_output[1] == None):
                    output = f_biblioteka.f_trim_output(ssh_output[0])
                    tmp_dict[ip]['ssh:cmd'] = f'<b>{cmd}</b>'
                    tmp_dict[ip]['ssh'] = f'{output}'

                tmp_dict[ip]['wskazowka:nmap'] = f'nmap --script ssh-brute -d {ip}'
                if AGGRESIVE:
                    f_biblioteka.f_zapis_log(
                                    f"port {port}",
                                    "subp",
                                    f"uruchamiam subprocess - nmap bruteforce ssh",
                                    pathLogFile=path_plik_logu)
                    #subprocess.Popen(["nmap","--script", "ssh-brute", ip, "-oA", path_file_data+"_nmap_"+ip+".txt"])
                    os.system(f"nmap --script ssh-brute -p{port} {ip} > {FILE_OUTPUT}_nmap_ssh_{ip}_{port}.txt &")
                    tmp_dict[ip]['Raport:nmap'] = f'<a href="{FILE_OUTPUT}_nmap_ssh_{ip}_{port}.txt">{f_biblioteka.f_raport_img()}</a><br />---<br />Time: ~10min<br />nmap --script ssh-brute -p{port} {ip}' 
                #---
                tmp_dict[ip]['wskazowka:patator'] = f"patator ssh_login host={ip} user=root password=FILE0 0=Rekonesans/dictionary/s_pass_admin.txt -x ignore:mesg='Authentication failed.'\nTime: ~0h 11min Rekonesans/dictionary/s_pass_admin.txt (>2300 row) <br />Time: ~1h 03min Rekonesans/dictionary/s_pass_13k.txt (>13700 row)"
                
            # port 23 telnet
            if(port == "23" or "telnet" in opis_nmap.lower()) and protokol.lower() == "tcp":
                tmp_dict[ip]['wskazowka:nmap'] = f"nmap --script telnet* -p{port} -d {ip}"
                
                if AGGRESIVE:
                    f_biblioteka.f_zapis_log(
                                    f"port {port}",
                                    "subp",
                                    f"uruchamiam subprocess - nmap bruteforce telnet-u",
                                    pathLogFile=path_plik_logu)
                    os.system(f"nmap --script telnet* -p{port} {ip} > {FILE_OUTPUT}_nmap_telnet_{ip}_{port}.txt &")
                    tmp_dict[ip]['Raport:nmap'] = f'<a href="{FILE_OUTPUT}_nmap_telnet_{ip}_{port}.txt">{f_biblioteka.f_raport_img()}</a><br />---<br />nmap --script telnet* -p{port} {ip}'
                #---
                tmp_dict[ip]['wskazowka:patator'] = f"patator telnet_login host={ip} inputs='FILE0\nFILE1' 0=Rekonesans/dictionary/s_user.lst 1=Rekonesans/dictionary/s_pass_admin.txt persistent=0 timeout=7 prompt_re='Username:|Password:' -x ignore:egrep='Login incorrect.+Username:'"

            # port 25 smtp
            # output_smtp = "none"
            if(port == "25" or "smtp" in opis_nmap.lower()) and protokol.lower() == "tcp":
                cmd = f'nmap --script smtp* -p25 {ip} -Pn -n'
                smtp_output = f_biblioteka.f_polecenie_uniwersalne(cmd)

                if(smtp_output[1] == None):
                    output = f_biblioteka.f_trim_output(smtp_output[0])
                    tmp_dict[ip]['smtp:cmd'] = f'<b>{cmd}</b>'
                    tmp_dict[ip]['smtp'] = f'{output}'

            # port 53 | UDP | DNS
            if(port == "53" or "dns" in opis_nmap.lower()) and protokol.lower() == "udp":
                cmd = f'dig ANY @{ip}'
                dig_output = f_biblioteka.f_polecenie_uniwersalne(cmd)

                if(dig_output[1] == None):
                    output = f_biblioteka.f_trim_output(dig_output[0])
                    tmp_dict[ip]['dns:dig:cmd'] = f'<b>{cmd}</b>'
                    tmp_dict[ip]['dns:dig'] = f'{output}'

            # port 135
            #output_dcerpc_p135 = "none"
            if(port == "135" or "dcerpc" in opis_nmap.lower()) and protokol.lower() == "tcp":
                output_dcerpc_p135 = f_biblioteka.f_rpc_p135(ip)
                tmp_dict[ip]['dcerpc'] = f'{output_dcerpc_p135}'

            # port 137 - 139 NetBIOS
            # output_enum4linux = "none"
            if(port == "139" or "netbios" in opis_nmap.lower()) and protokol.lower() == "tcp":
                cmd = f"enum4linux {ip}"
                enum4linux_output = f_biblioteka.f_polecenie_uniwersalne(cmd)

                if(enum4linux_output[1] == None):
                    output = f_biblioteka.f_trim_output(enum4linux_output[0])
                    tmp_dict[ip]['enum4linux:cmd'] = f'<b>{cmd}</b>'
                    tmp_dict[ip]['enum4linux'] = f'{output}'
                    tmp_dict[ip]['patator'] = f'patator smb_login host={ip} user=FILE0 password=FILE1 0=Rekonesans/dictionary/s_user.lst 1=Rekonesans/dictionary/s_pass_admin.txt -x ignore:fgrep=STATUS_LOGON_FAILURE'

            # 5900 vnc
            if(port == "5900" or "vnc" in opis_nmap.lower()) and protokol.lower() == "tcp":
                tmp_dict[ip]['curl:vnc'] = f"<i>patator vnc_login host={ip} port={port} password=FILE0 0='Rekonesans/dictionary/s_pass_4-8_vnc.txt' -t 1 -x ignore:fgrep!='Authentication failure' -x ignore:fgrep='Too many authentication failures' --max-retries 1 -x quit:code=0</i>"
            

            # 6443 kubernetes
            if(port == "6443") and protokol.lower() == "tcp":
                cmd = f"curl -sk https://{ip}:{port}/version --max-time {CURL_MAX_TIME} "
                kubernetes_output = f_biblioteka.f_polecenie_uniwersalne(cmd)

                if(kubernetes_output[1] == None):
                    output = f_biblioteka.f_trim_output(kubernetes_output[0])
                    tmp_dict[ip]['curl:kebernetes:cmd'] = f'<b>{cmd}</b>'
                    tmp_dict[ip]['curl:kebernetes'] = f'{output}'
            
            i += 1
            data['skan'].append(tmp_dict)

            ip_path_plik_json = f"{path_plik_json[:-5]}_{ip}_{port}.json"
            f_json.f_zapisz_dane_jako_json(tmp_dict, ip_path_plik_json)
            ip_path_plik_html = f"{path_plik_html[:-5]}_{ip}_{port}.html"
            f_json.f_parsuj_plik_json_na_html(ip_path_plik_json, ip_path_plik_html)

    # zapisuje dane do pliku *.json
    TResults = f_json.f_zapisz_dane_jako_json(data, path_plik_json)
    typ_komunikatu = ""
    if(TResults == "sukces"):
        typ_komunikatu = "info"
    else:
        typ_komunikatu = "error"
    
    f_biblioteka.f_zapis_log("wynik: f_zapisz_dane_jako_json", typ_komunikatu, TResults, pathLogFile=path_plik_logu)

    # zapisuje dane do pliku *.html
    f_json.f_parsuj_plik_json_na_html(path_plik_json, path_plik_html)
    handler_file_with_data.close()

#####################################################################################################################
if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='Rekonesans MM wersja 0.1b',
        formatter_class=argparse.RawTextHelpFormatter
        )

    parser.add_argument('-fin', '--file-input', action='store', dest='file_input', type=str, 
                        help='Ścieżke do pliku z danymi. Plik źródłowy')
    parser.add_argument('-fout', '--file-output', action='store', dest='file_output', type=str, 
                        help='Ścieżke do zapisu pliku z wynikami skanowania')
    parser.add_argument('-b', '--behavior', action='store', dest='scan_behavior', type=boolean, 
                        help='True = agresywny tryb skanowania, brak lub False nie agresywny tryb skanowania')
    parser.add_argument('-cmt', '--curl-max-time', action='store', dest='curl_max_time', type=int, 
                        help='Value of max timeout')
    parser.add_argument('-st', '--scan-tag', action='store', dest='scan_tag', type=str, 
                        help='frendly project (scan) name')
    
    args = parser.parse_args()

    

    if ('scan_behavior' not in args or not args.scan_behavior):
        AGGRESIVE=False
        print(f_biblioteka.style.YELLOW("Aggresive mode scan: default False, use -b True to change that"))
    elif(args.scan_behavior==True):
        AGGRESIVE=True

    if ('curl_max_time' not in args or not args.curl_max_time):
        CURL_MAX_TIME = 7
        print(f_biblioteka.style.YELLOW("curl --max-time default set to 7, use -cmt int to change that"))
    elif(args.curl_max_time != 7):
        CURL_MAX_TIME=args.curl_max_time
    
    if ('scan_tag' not in args or not args.scan_tag):
        scan_tag = 'projekt1'
        print(f_biblioteka.style.YELLOW("scan_tag default set to 'projekt1', use -st str to change that"))
    elif(args.curl_max_time != 7):
        TAG_OF_THE_SKAN=args.scan_tag

    if ('file_input' not in args or not args.file_input):
        parser.print_help()
        sys.exit(1)
    else:
        path_file_data = args.file_input

        # sprawdza czy plik istnieje
        if(os.path.isfile(path_file_data)):
            if ('file_output' not in args or not args.file_output):
                # wynik skanowania zostanie zapisany w lokalizacji pliku z danymi.
                print(f_biblioteka.style.YELLOW("[-fout] Nie wprowadzono docelowego miejsca zapisu przeznaczonego na wyniki. Zapis wyniku w lokalizacji pliku z danymi."), flush=True)   
                path_plik_logu = args.file_input + ".log"
                path_plik_json = args.file_input + ".json"
                path_plik_html = args.file_input + ".html"
            else:
                path_plik_logu = args.file_output + ".log"
                path_plik_json = args.file_output + ".json"
                path_plik_html = args.file_output + ".html"
                FILE_OUTPUT = args.file_output

            # wyswietlenie czasu rozpoczęcia skanowania
            start_script = f_biblioteka.f_czas()
            print(f_biblioteka.style.BLUE(f"Rozpoczynam: {start_script}"), flush=True) 

            # zapis do logu
            f_biblioteka.f_zapis_log('main','info',start_script,pathLogFile=path_plik_logu)

            # wywolujemy funkcje, ktora odczyta plik z danymi linijka po linijce
            f_biblioteka.f_zapis_log(
                "f_odczyt_pliku_nmap",
                "info",
                f"odczytuje plik z danymi: {path_file_data}",
                pathLogFile=path_plik_logu)

            f_odczyt_pliku_nmap(path_file_data)
        else:
            print(f_biblioteka.style.RED(f"[-fin] Plik z danymi [{path_file_data}] nie istnieje!"))
            sys.exit(1) 
