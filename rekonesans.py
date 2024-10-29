###############################################################################
# rekonesans v0.2
# Written by MM
# Copyright 2021
#---
# nmap -sV -A -O -p- XcelX -oA PlikWynikowy
#---
# services -u -O 1 -c  port,proto,name,info -o /home/user/targets_ports - sort by host
# services -u -O 2 -c  port,proto,name,info -o /home/user/targets_ports - sort by port
# eyewitnes: cat msf_ports_inside2.txt|sed 's/"//g'|cut -d "," -f 1,2|sed "s/,/:/g" > host_ports2.txt
# while read -r line;do l=$(printf "%s" "$line" |tr -d '\r'|tr -d '\n'); printf "$l;"; curl -m 5 -k -L http://$l -i -s -o /dev/null -w "%{http_code}";echo;done < host_ports2.txt 
# ipinfo: while read -r line;do l=$(printf "%s" "$line" |tr -d '\r'|tr -d '\n'); echo "$l;"; curl -m 5 -k -L https://ipinfo.io/$line;echo;echo;done < Documents/PGE/outside/outside_addr_ip.txt > Documents/PGE/outside/ipinfo
# nmap: while read -r line;do l=$(printf "%s" "$line" |tr -d '\r'|tr -d '\n'|tr -d '\n'|tr -d '\t');nmap -n -Pn -p- $line -oA $line -v;done < ...
###############################################################################
import os
import argparse
import sys
import f_biblioteka

def f_odczyt_pliku(data_file, results_path):
    # How many services we will check
    line_count = f_biblioteka.count_lines_in_file(data_file)

    # open file with data   
    handler_data_file = open(data_file, 'r')

    # services counter
    i = 1

    todo_file = data_file+".done"
    todo_lines = 1;
    
    try:
        with open(todo_file,"r") as file_done:
            #last_line = file_done.readlines()[-1]
            for line in file_done:
                todo_lines+=1
    except:
        with open(todo_file,"w") as file_done:
            file_done.write("")
            

    # read from file line by line
    read_from_line = 0
    for service_info in handler_data_file:
        read_from_line+=1
        if (read_from_line >= todo_lines):
            print(f"service_info: {service_info}")
            (ip, port, protokol, usluga, opis_nmap) = service_info.replace("\"","").lower().strip().split(',')
            
            with open(todo_file,"a+") as file_done:
                file_done.write(f"{service_info.strip()}\n")

            # check if line from file is ip addr
            if ip.count(".") == 0:
                if f_biblioteka.extract_ip_addresses(ip) is None:
                    line_count -= 1
                    print(f"[-] IP addr: [{ip}] is incorrect")
            else:
                # execute command socat
                f_biblioteka.f_make_thread(f_biblioteka.f_socat, ip, port, protokol, usluga, opis_nmap, results_path)
                
                # execute command amap
                f_biblioteka.f_make_thread(f_biblioteka.f_amap, ip, port, protokol, usluga, opis_nmap, results_path)
                
                if(protokol.lower() == "tcp"):
                    # Get banner
                    f_biblioteka.f_make_thread(f_biblioteka.get_tcp_banner, ip, port, protokol, usluga, opis_nmap, results_path)
        
                    # CURL check http code
                    lista_protokol = ["http","https"]
                    lista_http_code = [200,204,301,302,307,401,403,404,405,500]

                    for proto in lista_protokol:
                        results_from_http = f_biblioteka.f_http_code(ip, port, proto, usluga, opis_nmap, results_path)
                        http_addr, http_code = results_from_http[0]

                        if http_code in lista_http_code:
                            # screenshot
                            f_biblioteka.f_make_thread(f_biblioteka.f_screen_shot_web, ip, port, proto, usluga, opis_nmap, results_path)

                            # get links from web
                            f_biblioteka.f_make_thread(f_biblioteka.f_get_links_from_web, ip, port, proto, usluga, opis_nmap, results_path)
                elif(protokol == "udp"):             
                    # Get banner
                    #f_biblioteka.get_udp_banner(ip, port, protokol, usluga, opis_nmap, results_path)
                    pass
                    
                f_biblioteka.f_make_index(data_file, results_path)          

    handler_data_file.close()
    return

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
            start_script = f_biblioteka.f_czas()

            # path to save results 
            path_to_results = os.path.dirname(path_file_data)

            # read data file line by line
            f_odczyt_pliku(path_file_data, path_to_results)
        else:
            print(f_biblioteka.style.RED(f"[-] Data file [{path_file_data}] do not exists!"))
            sys.exit(1) 