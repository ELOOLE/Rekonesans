import argparse
import sys
import ipaddress
import requests
import os


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def port_table(prange):
    if prange:
        p_table = list(range(65535))
    else:    
        p_table = ["80","81","82","83","6443","7443","8000","8080","8081","8443","9090","9091","9443","18450","19712"]
    return p_table

def proto_table():
    #pro_table = ["http://","https://"]
    pro_table = ["http://"]
    return pro_table

def scan_host(addr, ports):
    addr = addr.strip()
    if(validate_addr(addr)):
        print(f"[*] Start scaning {addr}")
        
        for protocol in proto_table():
            for port in port_table(prange=ports):
                #print(f"[*] {protocol}{addr}:{port}")
                sys.stdout.write("Current port: %s   \r" % (port) )
                sys.stdout.flush()
                respond = get_http_code_respond(f"{protocol}{addr}:{port}")
                try:
                    http_code = respond.status_code
                    if http_code != "000": 
                        headers = respond.headers
                        result = f"[+] http code {http_code} addr: {protocol}{addr}:{port}, headers:{headers}"
                        print(result)
                        with open("log_http_code", "+a") as results_file:
                            results_file.write(result)
                            results_file.write("\n")
                except:
                    pass
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
        return requests.get(url, verify=False, timeout=3)
    except Exception as e:
        return "error"


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
    
