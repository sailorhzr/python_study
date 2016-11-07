#!/usr/bin/env python
#this is ca test tool group

import sys,os,commands,time,shutil

CA_conf ="/root/CA/output/conf/mirror-ca.conf"

#settings
rrd_dir_list=["/home/disk0/ca-rrd/","/home/disk1/ca-rrd/","/home/disk2/ca-rrd/","/home/disk3/ca-rrd/","/home/disk4/ca-rrd/"]
#rrd_dir_list=["/root/a/","/root/b/","/root/c/"]

#disk clean
def disk_clean(rrd_dir_list,key): 
    if key == "all":
	for folder in rrd_dir_list:
	    try:
		shutil.rmtree(folder)
		print "del %s ... " %(folder)
	    except Exception,e:
		print "del %s err:"%(folder) ,e

    if key == "rrd":
	for folder in rrd_dir_list:
	    print "clean folder %s ... " %(folder)
	    filelist = os.listdir(folder)
	    for f in filelist:
		if f.endswith("rrd"):
		    fpath = os.path.join(folder,f)
		    try:
			os.remove(fpath)
			print "del %s ... " %(f)
		    except Exception,e:
			print "del %s err:"%(f) ,e
    else:
	usage()


#ip_num_search
def ip_list(rrd_dir_list,search_ip):
    ip_list = []
    for folder in rrd_dir_list:
	for file in os.listdir(folder):
	    if os.path.basename(file).endswith("rrd"):
		full_file_name = os.path.basename(file)
		ip = full_file_name[:full_file_name.index("-")]
		if search_ip == 'all':
		    print folder + ip
		ip_list.append(ip)
    print "total ip num: ",len(ip_list)
    if  ip_list.count(search_ip) != 0: 
	print "Include %s: %s"%(search_ip,ip_list.count(search_ip))
    elif search_ip != 'all':
	    print "Not find %s: " %(search_ip)


#main
def usage():
    print "usage: %s -c [ all | rrd ]	#clean disk"
    print "     : %s -i {$ip}	        #check ip in rrd file"
    sys.exit(1)

try:
    if sys.argv[1] == '-c':
	disk_clean(rrd_dir_list,sys.argv[2])   #done
    if sys.argv[1] == '-i':
	ip_list(rrd_dir_list,sys.argv[2])

except Exception,e:
    usage()





