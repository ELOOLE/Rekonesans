import f_biblioteka


def f_odczyt_pliku(data_file, results_path):
    # How many services we will check
    line_count = f_biblioteka.f_policz_wiersze_w_pliku(data_file)
    print(f"[i] {line_count} sum of all rows in file")

    # open file with data   
    handler_data_file = open(data_file, 'r')

    # counter of services
    i = 1

    # read from file line by line
    for service_info in handler_data_file:
        (ip, port, protokol, usluga, opis_nmap) = service_info.replace("\"","").lower().strip().split(',')
              
        if f_biblioteka.extract_ip_addresses(ip) is None:
            line_count -= 1
            print(f"[-] adres ip: [{ip}] niepoprawny")
        else:
            if(protokol.lower() == "tcp"):
                # Get banner
                gb = f_biblioteka.get_tcp_banner(ip=ip, port=port)
                f_biblioteka.print_result(gb,ip,port,0)
                f_biblioteka.save_results_in_file(gb, ip, port, protokol,usluga, opis_nmap, results_path, "banner grabbing")

                if "error" not in str(gb).lower():
                    # execute command socat
                    socat_output = f_biblioteka.f_socat(protokol, ip, port)
                    f_biblioteka.print_result(socat_output,ip,port,0)
                    f_biblioteka.save_results_in_file(socat_output, ip, port, protokol,usluga, opis_nmap, results_path, "execute command socat")
                    
                    # execute command amap
                    amap_output = f_biblioteka.f_amap(protokol, ip, port)
                    f_biblioteka.print_result(amap_output,ip,port,0)
                    f_biblioteka.save_results_in_file(amap_output, ip, port, protokol,usluga, opis_nmap, results_path, "execute command amap")
            elif(protokol == "udp"):             
                # Get banner
                gb = f_biblioteka.get_udp_banner(ip=ip, port=port)
                print(f"[*] ip:{ip}:{port} {gb}")
                f_biblioteka.save_results_in_file(gb, ip, port, protokol,usluga, opis_nmap, results_path, "banner grabbing")
                
                if "error" not in str(gb).lower():
                    # execute command socat
                    socat_output = f_biblioteka.f_socat(protokol, ip, port)
                    f_biblioteka.print_result(socat_output,ip,port,0)
                    f_biblioteka.save_results_in_file(socat_output, ip, port, protokol,usluga, opis_nmap, results_path, "execute command socat")

        f_biblioteka.f_make_index(data_file, results_path)
    return


