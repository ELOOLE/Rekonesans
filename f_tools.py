import requests
requests.packages.urllib3.disable_warnings()

from f_biblioteka import f_polecenie_uniwersalne, random_ua, f_trim_output

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

            # Making a get request
            response = requests.get(adres, verify=False, headers=UA, timeout=CURL_MAX_TIME, allow_redirects=False)
            
            return response.status_code


def f_curl2():
            # CURL FULL RESPONSE
            lista_http_code = ['200','301','302','404']
            if(http_code in lista_http_code):
                cmd = f"curl -I -k -s {h_prot}://{ip}:{port} --max-time {CURL_MAX_TIME} --no-keepalive"
                curl_output = f_biblioteka.f_polecenie_uniwersalne(cmd)
                if(curl_output[1] == None):
                    output = f_biblioteka.f_trim_output(curl_output[0])
                    tmp_dict[ip][f'curl:{h_prot}:cmd'] = f'<b>{cmd}</b>'
                    tmp_dict[ip][f'curl:{h_prot}:info'] = f'{output}'
                
                try:
                    # screenshot
                    output_screen_shot_web = f_biblioteka.f_screen_shot_web(adres, path_plik_logu)
                    if(output_screen_shot_web == "error"):
                        tmp_dict[ip][f'web_shot'] = f'{output_screen_shot_web}\n'
                    else:
                        tmp_dict[ip][f'web_shot'] = f'<img src="{output_screen_shot_web}">\n'

                    # zbierz linki ze strony
                    if(http_code == "200"):
                        output_links_from_web = f_biblioteka.f_get_links_from_web(adres)
                        tmp_dict[ip][f'links:{h_prot}'] = f'{output_links_from_web}\n'

                    # przekierowanie
                    if(http_code == "301" or http_code == "302"):
                        redirect_url = ""
                        cmd = "curl -I -k -s -o /dev/null -w \"%{redirect_url}\" " + f" --max-time {CURL_MAX_TIME} {adres}"
                        curl_output = f_biblioteka.f_polecenie_uniwersalne(cmd)
                        if(curl_output[1] == None):
                            redirect_url = curl_output[0].decode('utf-8')
                            tmp_dict[ip][f'curl:{h_prot}:redirect_url:cmd'] = f'<b>{cmd}</b>'
                            tmp_dict[ip][f'curl:{h_prot}:redirect_url:addr'] = f'{redirect_url}'

                            cmd = "curl -I -k -s -o /dev/null -w \"%{http_code}\" " + f" --max-time {CURL_MAX_TIME} {redirect_url}"
                            curl_output = f_biblioteka.f_polecenie_uniwersalne(cmd)
                            
                            http_code = "000"
                            if(curl_output[1] == None):
                                http_code = curl_output[0].decode('utf-8')
                                tmp_dict[ip][f'curl:{h_prot}:redirect_url_follow:cmd'] = f'<b>{cmd}</b>'
                                tmp_dict[ip][f'curl:{h_prot}:redirect_url_follow:http_code'] = f'{http_code}'

                                if(http_code == "200" or http_code== "404"):
                                    # screenshot
                                    output_screen_shot_web = f_biblioteka.f_screen_shot_web(redirect_url, path_plik_logu)
                                    if(output_screen_shot_web == "error"):
                                        tmp_dict[ip][f'web_shot:redirect_url'] = f'{output_screen_shot_web}\n'
                                    else:
                                        tmp_dict[ip][f'web_shot:redirect_url'] = f'<img src="{output_screen_shot_web}">\n'

                                if(http_code == "200"):
                                    # linki
                                    output_links_from_web = f_biblioteka.f_get_links_from_web(redirect_url)
                                    tmp_dict[ip][f'links:{h_prot}:redirect_url'] = f'{output_links_from_web}\n'
                except Exception as er:
                    f_biblioteka.f_zapis_log(
                        "f_odczyt_pliku_nmap/f_screen_shot_web",
                        "error",
                        f"Wyjatek scr shot {h_prot}://{ip}:{port} {str(er)}",
                        pathLogFile=path_plik_logu)
                    output_screen_shot_web = "none"

                # zapis do pliku *.json
                tmp_dict[ip]['wskazowka:nikto'] = f'nikto -h {ip}\n'
                tmp_dict[ip]['wskazowka:dirb'] = f'dirb {h_prot}://{ip} /usr/share/wordlists/dirb/common.txt\n'
                tmp_dict[ip]['wskazowka:crawl:wget'] = f'wget --wait=2 --level=inf --limit-rate=20K --recursive --page-requisites --user-agent=Mozilla --no-parent --convert-links --adjust-extension --no-clobber -e robots=off {h_prot}://{ip}:{port} --no-check-certificate'
                tmp_dict[ip]['wskazowka:FUZZ:ffuf'] = f'ffuf -w Rekonesans/dictionary/s_web_fuzz.txt -u {h_prot}://{ip}:{port}/FUZZ'
    else:
        return "", "UDP so don't checking..."