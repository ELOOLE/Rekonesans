

import argparse
import json
import os

from json2html import *

def f_parsuj_plik_json_na_html(srcfile, dstfile):
    try:
        data = []
        uchwyt_plik_json = open(srcfile, 'r')
        data = json.load(uchwyt_plik_json)

        #print(str(type(data)))

        raport_html = open(dstfile, 'w')
        raport_html.write(json2html.convert(data, table_attributes='width="100%"', clubbing=True, encode=False, escape=True))
        raport_html.close()
             
        f_html_parser(dstfile)
        wynik = "sukces"
    except Exception as e:
        print(e)
        wynik = str(e)


    return wynik

def f_html_parser(file_html):
    file_html_new = file_html[:-5] + "_convert.html"

    open_file_html = open(file_html, "r")
    open_file_html_new = open(file_html_new, "w+")

    head = '<!DOCTYPE html> \n'
    head += '<html>\n'
    head += '<head>\n'
    head += '<style>\n'
    head += 'table, th, td {'
    head += 'font-family: "Lucida Console", Monaco, monospace;'
    head += 'border: 1px solid #1C6EA4;'
    head += 'background-color: #EEEEEE;'
    head += 'width: 100%;'
    head += 'text-align: left;'
    head += 'border-collapse: collapse;}'
    head += 'th {text-align: right; width: 5%;}\n'
    head += '</style>\n'
    head += '</head>\n'
    head += '<body>\n'
    head += '<table>\n'
    head += '<tr>\n'
    head += '<td>\n'
    head += '<h5 style="text-align:right">autor: MM, wersja 0.1 2021 r.</h5>\n'
    head += '<hr>\n'
    head += f'<h1 style="text-align:center">Rekonesans XXX uslug.</h1>\n'
    head += '<hr>\n'
    head += f'SRT: <br/>END: \n'
    head += '<hr>\n'
    head += f'Plik logu: \n'
    head += '<br />\n'
    head += f'Bledow w pliku logu: \n'
    head += '</td>\n'
    head += '</tr>\n'
    head += '</table>\n'

    open_file_html_new.write(head)

    for line in open_file_html:
        line = line.replace("&gt;", ">")
        line = line.replace("&lt;", "<")
        line = line.replace("&amp;", "&")
        line = line.replace('&quot;', '"')
        line = line.replace('&#x27;',"'")
        line = line.replace('"<','')
        line = line.replace('\\r\\n','<br>')
        line = line.replace('\\n','<br>')
        line = line.replace('</td>','</td>\n')
        line = line.replace('</table>','</table>\n')
        
        open_file_html_new.write(line)

    foot = "\n</body>\n</html>"    
    open_file_html_new.write(foot)

    open_file_html.close()
    open_file_html_new .close()

if __name__ == '__main__':
    '''MAIN'''
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='JSON file to HTML file', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--fin', '--file-input', type=str, help='Podaj sciezke do pliku z json')
    #parser.add_argument('--fout', '--file-output', type=str, help='Sciezka do zapisu pliku z wynikami skanowania')
    args = parser.parse_args()

    # odczyt pliku
    if(str(args.fin) == '' or str(args.fin) == 'None'):
        path_plik_nmap_msfconsole = '/home/pentester/Dokumenty/PPL/ppl_new7.json'
    else:
        path_plik_nmap_msfconsole = args.fin
    
    if(os.path.isfile(path_plik_nmap_msfconsole)):
        '''sprawdza czy plik istnieje'''
        path_plik_html = path_plik_nmap_msfconsole + ".html"

        # wywolujemy funkcje, ktora odczyta nam plik linijka po linijce
        f_parsuj_plik_json_na_html(path_plik_nmap_msfconsole, path_plik_html)
    else:
        print("Plik z danymi nie istnieje!" + path_plik_nmap_msfconsole)
