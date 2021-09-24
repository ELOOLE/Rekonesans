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

    open_file_html_new.write(head)

    for line in open_file_html:
        line = line.replace("&gt;", ">")
        line = line.replace("&lt;", "<")
        line = line.replace("&amp;", "&")
        line = line.replace('&quot;', '"')
        line = line.replace('&#x27;',"'")
        line = line.replace('"<','')
        line = line.replace('\\r\\n','<br />')
        line = line.replace('\\n','<br />')
        line = line.replace('</td>','</td>\n')
        line = line.replace('</table>','</table>\n')
        
        open_file_html_new.write(line)

    foot = "\n</body>\n</html>"    
    open_file_html_new.write(foot)

    open_file_html.close()
    open_file_html_new .close()
