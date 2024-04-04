import f_biblioteka
import threading

def f_odczyt_pliku(data_file, results_path):
    # How many services we will check
    line_count = f_biblioteka.f_policz_wiersze_w_pliku(data_file)

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
                #f_biblioteka.f_socat(ip, port, protokol, usluga, opis_nmap, results_path)
                my_thread1 = threading.Thread(target=f_biblioteka.f_socat, args=(ip, port, protokol, usluga, opis_nmap, results_path))
                my_thread1.start()
                my_thread1.join()
                
                # execute command amap
                #f_biblioteka.f_amap(ip, port, protokol, usluga, opis_nmap, results_path)
                my_thread2 = threading.Thread(target=f_biblioteka.f_amap, args=(ip, port, protokol, usluga, opis_nmap, results_path))
                my_thread2.start()
                my_thread2.join()
                
                if(protokol.lower() == "tcp"):
                    # Get banner
                    my_thread3 = threading.Thread(target=f_biblioteka.get_tcp_banner, args=(ip, port, protokol, usluga, opis_nmap, results_path))
                    my_thread3.start()
                    my_thread3.join()
                    #f_biblioteka.get_tcp_banner(ip, port, protokol, usluga, opis_nmap, results_path)
        
                    # CURL check http code
                    lista_protokol = ["http", "https"]
                    lista_http_code = [200,204,301,302,307,401,403,404,405,500]

                    for proto in lista_protokol:
                        http_addr, http_code = f_biblioteka.f_http_code(ip, port, proto, usluga, opis_nmap, results_path)[0]

                        if http_code in lista_http_code:
                            # screenshot
                            try:
                                output_screen_shot_web = f_biblioteka.f_screen_shot_web(http_addr, results_path)

                                if(output_screen_shot_web[0] == "error"):
                                    f_biblioteka.print_result("[-] fail of maiking web shot",ip,port,2)
                                else:
                                    pic_file_img_html = f'<img src="{results_path}/{ip}_{port}_{proto}.jpg">'
                                    f_biblioteka.save_results_in_file(pic_file_img_html, ip, port, proto, usluga, opis_nmap, results_path, "webshot")
                                    pic_file = f'<a href="{results_path}/{ip}_{port}_{proto}.jpg">{results_path}/{ip}_{port}_{proto}.jpg</a>'
                                    f_biblioteka.save_results_in_file(pic_file, ip, port, proto, usluga, opis_nmap, results_path, "webshot")
                                
                            except Exception as e:
                                pass

                            # get links from web
                            try:
                                output_links_from_web = f_biblioteka.f_get_links_from_web(http_addr)
                                f_biblioteka.save_results_in_file(output_links_from_web, ip, port, proto, usluga, opis_nmap, results_path, "grep links from web")
                            except Exception as e:
                                f_biblioteka.save_results_in_file("[-] fail of grab links from web", ip, port, proto, usluga, opis_nmap, results_path, "grep links from web")
                elif(protokol == "udp"):             
                    # Get banner
                    f_biblioteka.get_udp_banner(ip, port, protokol, usluga, opis_nmap, results_path)
                    
                f_biblioteka.f_make_index(data_file, results_path)          

        
    handler_data_file.close()
    return


