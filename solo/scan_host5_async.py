import argparse
import asyncio
import random
import sys
import time 
import aiohttp
from aiohttp.client import ClientSession
import requests
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
        sys.stdout.write(f"[*] url: %s   \r" % (url) )
        sys.stdout.flush()
        await asyncio.sleep(1)
        async with session.get(url, timeout=timeo, ssl=False, allow_redirects=True, max_redirects=3, headers=random_ua()) as response:
            result = await response.text()
        
            print(f"[+] Alive addr {url}")
            
            #print(f"[*] ----")
            #print(f"[*] {result}")
            #print(f"[*] ----")


async def check_all_urls(urls:list,timeo:int):
    my_conn = aiohttp.TCPConnector(ssl=False, limit=0, enable_cleanup_closed=True,keepalive_timeout=timeo)
    async with aiohttp.ClientSession(connector=my_conn) as session:
        tasks = []
        for url in urls:
            task = asyncio.create_task(check_single_url(url,session,timeo))
            #asyncio.ensure_future()
            tasks.append(task)           
            sys.stdout.write(f"[*] Adding addr: %s   \r" % (url) )
            sys.stdout.flush()
        print("")
        await asyncio.gather(*tasks,return_exceptions=True) # the await must be nest inside of the session

        #while True:

            # get the status of the task
        #    status = task.done()
            # report the status
        #    sys.stdout.write(f"[-] Task done: %s, {url}   \r" % (task.done()) )
        #    sys.stdout.flush()
        #    sys.stdout.write(f"[!] Task done: %s, {url}   \r" % (task.done()) )
        #    sys.stdout.flush()
            #print(f'>task done: {task.done()}')
            # check if the task is done
        #    if status:
        #        break 


############################################################################################################
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-sh', '--single-host', action='store', dest='single_host', type=str, help='scaning single host')
    parser.add_argument('-t', '--timeout', action='store', dest='timeout', type=int, help='timeout', default=5)
    args = parser.parse_args()

    if ('single_host' not in args or not args.single_host):
        parser.print_help()
        sys.exit(1)
    #with open("/home/user/Documents/zus/zus_addr.txt", "r") as dane:
    #    for line in dane:
    #        url = []
    #        addr = line.strip()
    #        for protocol in proto_table():
    #            for port in port_table(prange=True):
    #                url.append(f"{protocol}{addr}:{port}")
    #        print(f"\n[*] Scanning address: {addr}")
    #        asyncio.run(download_all(url))
    addr = args.single_host
    urls = []
    for protocol in proto_table():
        for port in port_table(list(range(65536))):
            urls.append(f"{protocol}{addr}:{port}")
    print(f"\n[*] Scanning address: {addr}")
    print(f"[*] URLS list: {len(urls)}")
    asyncio.run(check_all_urls(urls, args.timeout))