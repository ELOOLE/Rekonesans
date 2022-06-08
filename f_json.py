import json
from json2html import *

def f_zapisz_dane_jako_json(data, dstfile):
    wynik = ""
    try:
        with open(dstfile, 'a+') as outfile:
            json.dump(data, outfile)
        wynik = "sukces"
    except Exception as e:
        wynik = str(e)

    return wynik


def f_parsuj_dane_json_na_html(data, dstfile):
    wynik = ""
    try:
        raport_html = open(dstfile, 'w')
        raport_html.write(
            json2html.convert(
                json=data,
                table_attributes='width="100%"',
                clubbing=True,
                encode=False,
                escape=True))
        raport_html.close()
        f_html_parser(dstfile)
        wynik = "sukces"
    except Exception as e:
        wynik = str(e)

    return wynik


def f_parsuj_plik_json_na_html(srcfile, dstfile):
    wynik = ""
    try:
        plik_json = open(srcfile, 'r')
        odczyt_pliku = plik_json.read()
        raport_html = open(dstfile, 'w')
        raport_html.write(
            json2html.convert(
                json=odczyt_pliku,
                table_attributes='width="100%"',
                clubbing=True,
                encode=False,
                escape=True))
        raport_html.close()
        f_html_parser(dstfile)
        wynik = "sukces"
    except Exception as e:
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
    head += f'SRT: XXX<br/>END: XXX\n'
    head += '<hr>\n'
    head += f'Plik logu: XXX\n'
    head += '<br />\n'
    head += f'Bledow w pliku logu: XXXX\n'
    head += '</td>\n'
    head += '</tr>\n'
    head += '</table>\n'

    open_file_html_new.write(head)

    for line in open_file_html:
        line = line.replace("&gt;", ">")
        line = line.replace("&lt;", "<")
        line = line.replace("&amp;", "&")
        line = line.replace('&quot;', '"')
        line = line.replace('&#x27;', "'")
        line = line.replace('"<', '')
        line = line.replace('\\r\\n', '<br>')
        line = line.replace('\\n', '<br>')
        line = line.replace('</td>', '</td>\n')
        line = line.replace('</table>', '</table>\n')

        open_file_html_new.write(line)

    foot = "\n</body>\n</html>"
    open_file_html_new.write(foot)

    open_file_html.close()
    open_file_html_new .close()