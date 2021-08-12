import os

file_html = "/home/user/test1.html"
file_html_new = file_html[:-5] + "_convert.html"

open_file_html = open(file_html, "r")
open_file_html_new = open(file_html_new, "w+")

head = "<!DOCTYPE html>\n<html>\n<head>\n<style>\ntable, th, td {border: 1px solid black;}\nth {text-align: right; width: 5%;}\n</style>\n</head>\n<body>\n"

open_file_html_new.write(head)

for line in open_file_html:
	#read replace the string and write to output file
    line = line.replace('&gt;', '>')
    line = line.replace('&lt;', '<')
    line = line.replace('&quot;', '\"')
    line = line.replace('b&#x27;', '')
    line = line.replace('&#x27;<','<')
    line = line.replace('>\n<','><')
    #line = line.replace('\n\n', '')
    open_file_html_new.write(line)

foot = "</body>\n</html>"    
open_file_html_new.write(foot)

#close input and output files
open_file_html.close()
open_file_html_new .close()
