import argparse
import sys
import ipaddress
import requests
import os
import threading
import ctypes
libgcc_s = ctypes.CDLL('libgcc_s.so.1')
import time

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
 

def port_table(prange):
    if prange:
        p_table = list(range(65535))
    else:    
        p_table = ["80","81","82","83","6443","7443","8000","8080","8081","8443","9090","9091","9443","18450","19712"]
    return p_table

def proto_table():
    pro_table = ["https://"]
    return pro_table

def scan_host(addr, ports):
    addr = addr.strip()
    if(validate_addr(addr)):
        print(f"[*] Start scaning {addr}")
        threads = []

        #for protocol in proto_table():
        print(f"[*] Build threads")
        for port in port_table(prange=ports):
            #sys.stdout.write(f"[*] Current port: %s   \r" % (port) )
            #sys.stdout.flush()
            respond = threading.Thread(target=get_http_code_respond, args=(f"http://{addr}:{port}",), daemon=True)
            threads.append(respond)
            respond = threading.Thread(target=get_http_code_respond, args=(f"https://{addr}:{port}",), daemon=True)
            threads.append(respond)
    
        print(f"[*] Starting threads")
        i = 0; 
        for thread in threads:
            procent = (i*100)/(65535*2)
            sys.stdout.write(f"[*] progress %s %% \r" % (int(procent)) )
            sys.stdout.flush()
            thread.start()
            i = i+1
        
        print(f"[*] Join threads")
        for thread in threads:
            thread.join()
    else:
        print(f"[-] Scaning ip addr {addr} isn't valid")


def validate_addr(addr):
    try:
        ip_obj = ipaddress.ip_address(addr)
        return True
    except:
        return False


def get_http_code_respond(url):
    try:    
        respond = requests.get(url, verify=False, timeout=3)
        http_code = respond.status_code
        if http_code != "000": 
            headers = respond.headers
            result = f"[+] http code {http_code} addr: {url}, headers:{headers}"
            print(result)
            with open("log_http_code", "+a") as results_file:
                results_file.write(result)
                results_file.write("\n")
    except Exception as e:
        #print(f"error: {e}")
        pass

if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    parser = argparse.ArgumentParser()
    parser.add_argument('-sh', '--single-host', action='store', dest='single_host', type=str, help='scaning single host')
    parser.add_argument('-sn', '--subnetwork', action='store', dest='subnetwork', type=str, help='scaning subnetwork')
    parser.add_argument('-f', '--file', action='store', dest='file', type=str, help='scaning subnetwork/host from file')
    parser.add_argument('-a', '--all-ports', action='store', dest='ports', type=bool, default=False, help='port range')
    args = parser.parse_args()

    if ('single_host' not in args or not args.single_host) and ('subnetwork' not in args or not args.subnetwork) and ('file' not in args or not args.file):
        parser.print_help()
        sys.exit(1)
    
    if (args.single_host is not None) and (args.subnetwork is not None) and (args.file is not None):
        print("Set single host or subnetwork or file as source do scan")
        parser.print_help()
        sys.exit(1)

    if (args.single_host is not None):
        scan_host(args.single_host, args.ports)
    elif (args.subnetwork is not None):
        scan_host(args.subnetwork, args.ports)
    elif (args.file is not None):
        scan_host(args.file, args.ports)
    