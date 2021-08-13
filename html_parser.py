import os

file_html = "/home/user/test1.html"
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
    i = 1
    while(i > 0):
        if(line.find("&gt;") > 0):
            line = line.replace("&gt;", ">")
            i += 1
        else:
            i -= 1

    i = 1
    while(i > 0):    
        if(line.find("&lt;") > 0):
            i += 1
            line = line.replace("&lt;", "<")
        else:
            i -= 1

    i = 1
    while(i > 0):    
        if(line.find("&amp;") > 0):
            i += 1
            line = line.replace("&amp;", "&")
        else:
            i -= 1

    i = 1
    while(i > 0):  
        line = line.replace('&quot;', '"')
        if(line.find('&quot;') > 0):
            i += 1
        else:
            i -= 1
    
    i = 1
    while(i > 0):
        line = line.replace('&#x27;',"'")
        if(line.find('&#x27;') > 0):
            i += 1
        else:
            i -= 1

    i = 1
    while(i > 0):
        line = line.replace('"<','')
        if(line.find('"<') > 0):
            i += 1
        else:
            i -= 1
    
    i = 1
    while(i > 0):
        line = line.replace('\\r\\n','<br />')
        if(line.find('\\r\\n') > 0):
            i += 1
        else:
            i -= 1

    i = 1
    while(i > 0):
        line = line.replace('\\n','<br />')
        if(line.find('\\n') > 0):
            i += 1
        else:
            i -= 1

    line = line.replace('</td>','</td>\n')
    line = line.replace('</table>','</table>\n')
    
    open_file_html_new.write(line)

    #line = line.replace('\n\n', '')
    

foot = "\n</body>\n</html>"    
open_file_html_new.write(foot)

#close input and output files
open_file_html.close()
open_file_html_new .close()
