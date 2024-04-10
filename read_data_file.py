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
                    f_biblioteka.get_udp_banner(ip, port, protokol, usluga, opis_nmap, results_path)
                    
                f_biblioteka.f_make_index(data_file, results_path)          

    handler_data_file.close()
    return


