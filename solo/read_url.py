import socket
import requests
import urllib3
from colorama import init
from termcolor import colored
import texttable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_file(datafile):
    table = texttable.Texttable()
    table.header(["url", "ip", "http code", "https code"])
    table.set_cols_width([50,20,10,10])

    with open(datafile, "r") as h_datafile:
        

        for line in h_datafile:
            url = line.strip()
            ip = get_hostname_ip(url)
            
            if ip != "error":
                http_code = get_http_code_respond(f"http://{url}")
                https_code = get_http_code_respond(f"https://{url}")
                
            else:
                http_code = "---"
                https_code = "---"
                
            result = f"[*] url: {url}, [+] ip: {ip}, [*] http_code:{http_code}, [*] https_code:{https_code}"
            Tresults = [url, ip, http_code, https_code]
            table.add_rows([Tresults], header=False)
            print(result)
        
        print(table.draw())
            

def get_hostname_ip(fqdn):
    try:
        return socket.gethostbyname(fqdn)
    except Exception as e:
        return "error"


def get_http_code_respond(url):
    try:
        return requests.get(url, verify=False, timeout=7).status_code
    except Exception as e:
        return "error"
    

if __name__ == "__main__":
    read_file("/home/user/Documents/zus/zus1.txt")