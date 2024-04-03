import f_biblioteka


def f_odczyt_pliku(data_file, results_path):
    # How many services we will check
    line_count = f_biblioteka.f_policz_wiersze_w_pliku(data_file)

    # open file with data   
    handler_data_file = open(data_file, 'r')

    # services counter
    i = 1

    # read from file line by line
    for service_info in handler_data_file:
        (ip, port, protokol, usluga, opis_nmap) = service_info.replace("\"","").lower().strip().split(',')

        # check if line from file is ip addr
        if ip.count(".") == 0:
            if f_biblioteka.extract_ip_addresses(ip) is None:
                line_count -= 1
                print(f"[-] IP addr: [{ip}] is incorrect")
        else:
            #print(f"[i] {line_count} sum of all rows in file")
            if(protokol.lower() == "tcp"):
                # Get banner
                gb = f_biblioteka.get_tcp_banner(ip=ip, port=port)
                f_biblioteka.print_result(gb,ip,port,0)
                f_biblioteka.save_results_in_file(gb, ip, port, protokol,usluga, opis_nmap, results_path, "banner grabbing")

                # execute command socat
                socat_output = f_biblioteka.f_socat(protokol, ip, port)
                f_biblioteka.print_result(socat_output,ip,port,0)
                f_biblioteka.save_results_in_file(socat_output, ip, port, protokol,usluga, opis_nmap, results_path, "execute command socat")
                
                # execute command amap
                amap_output = f_biblioteka.f_amap(protokol, ip, port)
                f_biblioteka.print_result(amap_output,ip,port,0)
                f_biblioteka.save_results_in_file(amap_output, ip, port, protokol,usluga, opis_nmap, results_path, "execute command amap")
                
                # CURL check http code
                lista_protokol = ["http", "https"]
                lista_http_code = [200,204,301,302,307,401,403,404,405,500]

                for proto in lista_protokol:
                    http_code_output = f_biblioteka.f_http_code(proto, ip, port, 7)
                    f_biblioteka.print_result(http_code_output,ip,port,0)
                    f_biblioteka.save_results_in_file(http_code_output, ip, port, protokol, usluga, opis_nmap, results_path, "http return code")

                    # http: addr, code
                    http_addr, http_code = http_code_output

                    if http_code in lista_http_code:
                        print(f"[+] http code: {http_code_output[1]}")

                        # screenshot
                        try:
                            output_screen_shot_web = f_biblioteka.f_screen_shot_web(http_addr, results_path)

                            print(output_screen_shot_web)

                            if(output_screen_shot_web == "error"):
                                f_biblioteka.print_result("[-] fail of maiking web shot",ip,port,2)
                            else:
                                f_biblioteka.print_result("[+] successful of maiking web shot",ip,port,1)
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
                            f_biblioteka.print_result("[-] fail of grab links from web",ip,port,2)
                            f_biblioteka.save_results_in_file("[-] fail of grab links from web", ip, port, proto, usluga, opis_nmap, results_path, "grep links from web")
            elif(protokol == "udp"):             
                # Get banner
                gb = f_biblioteka.get_udp_banner(ip=ip, port=port)
                print(f"[*] ip:{ip}:{port} {gb}")
                f_biblioteka.save_results_in_file(gb, ip, port, protokol,usluga, opis_nmap, results_path, "banner grabbing")
                
                # execute command socat
                socat_output = f_biblioteka.f_socat(protokol, ip, port)
                f_biblioteka.print_result(socat_output,ip,port,0)
                f_biblioteka.save_results_in_file(socat_output, ip, port, protokol,usluga, opis_nmap, results_path, "execute command socat")
            
            f_biblioteka.f_make_index(data_file, results_path)            
    return


