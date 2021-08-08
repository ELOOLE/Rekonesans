import os

file_html = "/home/nano/test1.html"
file_html_new = file_html[:-5] + "_convert.html"

open_file_html = open(file_html, "r")
open_file_html_new = open(file_html_new, "w+")

for line in open_file_html:
	#read replace the string and write to output file
    line = line.replace('&gt;', '>')
    line = line.replace('&lt;', '<')
    line = line.replace('&quot;', '\"')
    line = line.replace('b&#x27;&#x27;', 'none')
    #line = line.replace('\n\n', '')
    open_file_html_new.write(line)
    

#close input and output files
open_file_html.close()
open_file_html_new .close()
