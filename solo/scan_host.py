import argparse
import asyncio
import datetime
import json
import os
import random
import socket
import sys
import time
from urllib import request 
import aiohttp
from aiohttp.client import ClientSession
try: 
    import jarm
except Exception as e:
    print("[-] jarm not loaded")
    pass
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    mozilla_version = "Mozilla/5.0"  
    os = USER_AGENT_PARTS.get('os')[random.choice(list(USER_AGENT_PARTS.get('os').keys()))]
    os_name = random.choice(os.get('name'))
    sysinfo = os_name
    
    platform = USER_AGENT_PARTS.get('platform')[random.choice(list(USER_AGENT_PARTS.get('platform').keys()))]
    
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
    return {'User-Agent': ua_string}


def port_table(prange):
    #if prange:
    #    p_table = list(range(65536))
    #else:    
        #p_table = ["80","81","82","83","6443","7443","8000","8080","8081","8443","9090","9091","9443","18450","19712"]
    return prange


def proto_table() -> str:
    pro_table = ["http://","https://"] 
    return pro_table


sem = asyncio.Semaphore(256)

async def check_single_url(url:str,session:ClientSession,timeo:int):
    async with sem:
        sys.stdout.write(f"[*] Url: %s   \r" % (url) )
        sys.stdout.flush()
        await asyncio.sleep(1)
        async with session.get(url, timeout=timeo, ssl=False, allow_redirects=True, max_redirects=3, headers=random_ua()) as response:
            result = await response.text() # do zapisania, niewykorzystane
            # take screen / web shot
            print(f"[+] Alive addr {url}")
            try:
                if "https" in url:
                    url = url.replace("https://","")
                    addr, port = url.split(":")
                    if int(port) > 0:
                        #print(f"[i] {addr}:{port}")
                        jarm.smain(addr, int(port))
            except Exception as e:
                #print(f"[-] jarm: none: {e}")
                pass

async def check_all_urls(urls:list,timeo:int):
    my_conn = aiohttp.TCPConnector(ssl=False, limit=0, enable_cleanup_closed=True,keepalive_timeout=timeo)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(check_single_url(url,session,timeo))
            tasks.append(task)           
            sys.stdout.write(f"[*] Adding addr: %s   \r" % (url) )
            sys.stdout.flush()
        print("")
        await asyncio.gather(*tasks,return_exceptions=True)

############################################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-sh', '--single-host', action='store', dest='single_host', type=str, help='scaning single host')
    parser.add_argument('-t', '--timeout', action='store', dest='timeout', type=int, help='timeout', default=5)
    parser.add_argument('-cip', '--check-ip', action='store', dest='check_ip', type=bool, help='check if ip was scanned', default='true')
    args = parser.parse_args()

    time_start = time.time()

    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)

    if ('single_host' not in args or not args.single_host):
        parser.print_help()
        sys.exit(1)

    # check if data file exists
    path_to_ip = f"{script_directory}/ip.txt"

    #print(f"[*] Path to ip file: {path_to_ip.strip()}")

    addr = args.single_host
    urls = []
    for protocol in proto_table():
        for port in port_table(list(range(65536))):
            urls.append(f"{protocol}{addr}:{port}")
    
    
    date_of_scan = str(datetime.datetime.now())
    
    try:
        addr_ip = socket.gethostbyname(addr)
        #print(f"[*] IPv4 address: {addr_ip}")
    except Exception as e:
        #print(f"[-] IPv4 address: none\n")
        sys.exit(1)

    with open(path_to_ip, "r") as data_ip:
        for item in data_ip:
            ip, datas = item.split(";")

            if addr_ip == ip:
                #print(f"[-] Address {ip.strip()} was checked {datas}")
                sys.exit(1)
               
    with open(path_to_ip, "a+") as data_ip:
        print(f"[*] Scanning address: {addr}")
        print(f"[*] Scanning date: {date_of_scan}")
        print(f"[*] IPv4 address: {addr_ip}")
        data_ip.write(f"{addr_ip};{date_of_scan}\n")

    try:
        addr_hostname = socket.gethostbyaddr(addr_ip)
        #print(f"[+] Hostname: {addr_hostname}")
        for item in addr_hostname:
            print(f"[+] Hostname: {item}")
    except Exception as e:
        #print(f"[-] Hostname: none")
        pass

    try:
        addr_nameinfo = socket.getnameinfo((addr_ip, 0), 0)
        #print(f"[+] getnameinfo: {addr_nameinfo}")
        for item in addr_nameinfo:
            print(f"[+] getnameinfo: {item}")
    except Exception as e:
        #print(f"[-] getnameinfo: none")
        pass
    
    try:
        addrinfo = socket.getaddrinfo(addr, 0, proto=socket.IPPROTO_TCP)
        #print(f"[+] addrinfo: {addrinfo}")
        for item in addrinfo:
            print(f"[+] addrinfo: {item}")
    except Exception as e:
        #print(f"[-] addrinfo: none")
        pass


    print(f"[*] Urls list to check: {len(urls)}")
    asyncio.run(check_all_urls(urls, args.timeout))

    time_end = time.time()

    print(f"\n[*] Execution time: {round((time_end - time_start)/60, 2)} minutes\n")
