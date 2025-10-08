import argparse
import sys
#from urllib import request
import socket

import requests
requests.packages.urllib3.disable_warnings()

def http_request(url, verify=True):
    try:
        response = requests.get(url, timeout=5, verify=verify)
        return response.status_code
    except Exception:
        return "-"

def read_file(file_location):
    with open(file_location) as h_file:
        for line in h_file:
            domena = line.strip()
            http_code = http_request(f'http://{domena}')
            https_code = http_request(f'https://{domena}', verify=False)
            try:
                ip = socket.gethostbyname(domena)
            except Exception:
                ip = "-"

            content = f'[*] {domena}, http: {http_code}, https: {https_code}, ip: {ip}'
            print(content)
            write_file(destination_data_file, content)

def write_file(file_location, content):
    with open(file_location, "a") as h_file:
        h_file.write(content + '\n')

'''
MAIN
'''        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='MM wersja 0.1b',
        formatter_class=argparse.RawTextHelpFormatter
        )
    
    parser.add_argument('-fin', '--file-input', action='store', dest='file_input', type=str, 
                        help='Path to file with data.')
    parser.add_argument('-fout', '--file-output', action='store', dest='file_output', type=str, 
                        help='Path to file where results will be stored')
    args = parser.parse_args()

    if ('file_input' not in args or not args.file_input):
        parser.print_help()
        sys.exit(1)
    else:
        source_data_file = args.file_input

    if ('file_output' not in args or not args.file_output):
        dst_data_file = source_data_file + '.out'
    else:
        destination_data_file = args.file_output

    read_file(source_data_file)
    print('[*] Done!')
