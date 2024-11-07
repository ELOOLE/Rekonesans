import argparse
import sys
import ipaddress
import requests


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def scan_host(addr):
    addr = addr.strip()
    if(validate_addr(addr)):
        print(f"[*] Start scaning {addr}")
        
        http_code = get_http_code_respond(f"http://{addr}")
        print(f"curl code {http_code}")
        
        https_code = get_http_code_respond(f"https://{addr}")
        print(f"curl code {https_code}")
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
        return requests.get(url, verify=False, timeout=5).status_code
    except Exception as e:
        return "error"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-sh', '--single-host', action='store', dest='single_host', type=str, help='scaning single host')
    parser.add_argument('-sn', '--subnetwork', action='store', dest='subnetwork', type=str, help='scaning subnetwork')
    parser.add_argument('-f', '--file', action='store', dest='file', type=str, help='scaning subnetwork/host from file')
    args = parser.parse_args()

    if ('single_host' not in args or not args.single_host) and ('subnetwork' not in args or not args.subnetwork) and ('file' not in args or not args.file):
        parser.print_help()
        sys.exit(1)
    
    if (args.single_host is not None) and (args.subnetwork is not None) and (args.file is not None):
        print("Set single host or subnetwork or file as source do scan")
        parser.print_help()
        sys.exit(1)

    if (args.single_host is not None):
        scan_host(args.single_host)
    elif (args.subnetwork is not None):
        scan_host(args.subnetwork)
    elif (args.file is not None):
        scan_host(args.file)
    