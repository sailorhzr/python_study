#!/usr/bin/env python
#read ds conf and list last 10 minutes packet store, export appoint file to new localtion.

import os,re,commands,sys
import time

#read ds conf
ds_conf_path = '/home/work/mirror-ds/output/conf/ds.conf'

if int(len(sys.argv)) == 2:
    if sys.argv[1].isdigit() == 1:  #isdigit return bool type. 1:True, 0:False
	print "aa: ",type(sys.argv[1].isdigit())
	minute_num = sys.argv[1]
    elif sys.argv[1] == '-x':
	print "use hexadecimal storge ..."
	minute_num = "10"
	oct = 1
    else:
	print "please input digit,default show 10 list ..."
	minute_num = "10"
else:
    minute_num = "10"
    
try:
    f = open(ds_conf_path)
except Exception ,e:
    print "open file error:",e
    sys.exit(-1)

path_list = []
try:
    line = f.readline()
    while line:
	if line.find('ip_path') != -1:
	    str=re.split('=',line)
#	    print str[1]
	    path_list.append(str[1].strip('\n'))
	line = f.readline()
except Exception,e:
    print "read file error:",e
    sys.exit(-1)
finally:
    f.close() 

#list last 10 file in every folder
##recover str to list
def str_to_list(str):
    if str[-1] != '\n':   #no "\n" after last file
	str = str + '\n'
    str_list = []
    j = ''
    for i in str:
	j = j + i
	if i == '\n':
	    str_list.append(j.strip('\n'))
	    j = ''  #reset temp str
    return str_list

def list_file(list):
    for file in list:
	file_sum= []
	for index in range(len(path_list)):
	    full_path = path_list[index] + file
	    file_size = os.path.getsize(full_path)
	    file_sum.append(file_size)
	   # print full_path, ":" , file_size
	print file,"    size:",sum(file_sum)

def show_list():
    ##get file str
    file_list = []
    #cmd='find ' + path_list[0] + ' -type f | xargs ls -lrt | tail -n ' + minute_num	 + '| awk -F / {\'print $NF\'}'  #do not use head, it will raise "ls: write error: Broken pipe" error.
    cmd = 'ls  -rt ' + path_list[0] + ' | tail -n ' + minute_num	 + '| awk -F / {\'print $NF\'}'  #do not use head, it will raise "ls: write error: Broken pipe" error.
    file = commands.getoutput(cmd) 	
    print "Last %s file name : \n"%(minute_num)
    list_file(str_to_list(file))

   # cmd_useful ='find ' + path_list[0] + ' -type f -size +24c | xargs ls -lrt | tail -n ' + minute_num	 + '| awk -F / {\'print $NF\'}'  #list last valid pcap file
   # file_useful = commands.getoutput(cmd_useful) 	
   # print "\nLast %s file name with vaild data : \n"%(minute_num)
   # list_file(str_to_list(file_useful))

while 1:
    show_list()
    cal_file = raw_input("open file (\"f\":flush list \"q\": quit):")
    if cal_file == 'q':
	sys.exit(1)
    if cal_file != 'f':
#    if sys.stdin.read() != '\n':
	break 

cal_output = sys.argv[0] + ".log"
try:
    f = open(cal_output,'w')
    for index in range(len(path_list)):
	cal_file_path = path_list[index] + cal_file
	#print cal_file_path
	if oct != 1:
	    cmd = 'tcpdump -nn -r ' + cal_file_path
	else:
	    cmd = 'tcpdump -nn -r ' + cal_file_path + ' -x'
	(status,output) = commands.getstatusoutput(cmd)
	if status != 0:
	    print "tcpdump file %s error: status: %s" %(cal_file_path,status)
	    continue
	print  "process ",cal_file_path ,"..."
	for i in str_to_list(output):
	    if i.find(path_list[index]) == -1:
		i = i + '\n'
		f.write(i)
    print "\ndump file: ", cal_output

except Exception,e:
    print "some error : ",e
    sys.exit (-1)
finally:
    f.close()

for count,line in enumerate(open(cal_output, 'rU')):
#	print count
#	print line 
    pass
count += 1
newcount = len(open(cal_output,'rU').readlines())
print "count : ", count
print "newcount : ", newcount
 


