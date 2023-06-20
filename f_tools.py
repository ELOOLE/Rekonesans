import requests
requests.packages.urllib3.disable_warnings()

from f_biblioteka import f_polecenie_uniwersalne, random_ua, f_trim_output, f_screen_shot_web, f_timed


@f_timed
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
    

@f_timed
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

            # Making a get request
            response = requests.get(adres, verify=False, headers=UA, timeout=CURL_MAX_TIME, allow_redirects=False)
            
            return adres, response.status_code