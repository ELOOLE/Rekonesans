###############################################################################
# rekonesans v0.2
# Written by MM
# Copyright 2021
#---
# nmap -sV -A -O -p- XcelX -oA PlikWynikowy
#---
# services -u -O 1 -c  port,proto,name,info -o /home/user/targets_ports - sort by host
# services -u -O 2 -c  port,proto,name,info -o /home/user/targets_ports - sort by port
###############################################################################
import os
import argparse
import sys
from f_biblioteka import style, f_czas, f_make_index
from read_data_file import f_odczyt_pliku


if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='Rekonesans MM wersja 0.1b',
        formatter_class=argparse.RawTextHelpFormatter
        )

    parser.add_argument('-fin', '--file-input', action='store', dest='file_input', type=str, 
                        help='Path to file with data.')
    parser.add_argument('-fout', '--file-output', action='store', dest='file_output', type=str, 
                        help='Path to file where results will be stored')
    parser.add_argument('-b', '--behavior', action='store', dest='scan_behavior', type=str, default=False,
                        help='True = agresywny tryb skanowania, brak lub False nie agresywny tryb skanowania')
    parser.add_argument('-cmt', '--curl-max-time', action='store', dest='curl_max_time', type=int, default=7,
                        help='Value of max timeout')
    args = parser.parse_args()

    if ('file_input' not in args or not args.file_input):
        parser.print_help()
        sys.exit(1)
    else:
        path_file_data = args.file_input

        # check if data file exists
        if(os.path.isfile(path_file_data)):
            start_script = f_czas()

            # path to save results 
            path_to_results = os.path.dirname(path_file_data)

            # read data file line by line
            f_odczyt_pliku(path_file_data, path_to_results)
        else:
            print(style.RED(f"[-] Data file [{path_file_data}] do not exists!"))
            sys.exit(1) 