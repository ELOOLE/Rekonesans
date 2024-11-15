import argparse
import random
import sys
import ipaddress
import requests
import os
import threading
import ctypes
libgcc_s = ctypes.CDLL('libgcc_s.so.1')
import time
import datetime

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def f_czas():
    '''Zwraca w wyniku aktualny czas'''
    return str(datetime.datetime.now())[:19]


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

            respond = threading.Thread(target=get_http_code_respond, args=(f"http://{addr}:{port}",))
            threads.append(respond)
            respond = threading.Thread(target=get_http_code_respond, args=(f"https://{addr}:{port}",))
            threads.append(respond)
    
        print(f"\n[*] Starting threads")
        i = 0; 
        for thread in threads:
            procent = (i*100)/(65535*2)
            sys.stdout.write(f"[*] progress %s %% \r" % (int(procent)) )
            sys.stdout.flush()
            thread.start()
            i = i+1
        
        print(f"\n[*] Join threads")
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

    print(f"[*] {f_czas()}")

    if (args.single_host is not None):
        scan_host(args.single_host, args.ports)
    elif (args.subnetwork is not None):
        scan_host(args.subnetwork, args.ports)
    elif (args.file is not None):
        scan_host(args.file, args.ports)
    
    print(f"[*] {f_czas()}")
    