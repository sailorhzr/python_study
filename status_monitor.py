#!/usr/bin/env python
#description: this script will monitor system CPU/memory/disk usage/file open number/hosteye status etc
#hanzurong@baiud.com (2016-07-01)

import os,sys,re,time
import commands
import logging

#defin log format
log_file=__file__+".log"
log_format='[%(asctime)s][%(levelname)s][%(funcName)s]: %(message)s'
logging.basicConfig(filename=log_file,format=log_format,level=logging.DEBUG)

#expect resource limit
cpu_limit=10.0	    #10%
mem_limit=51200	    #KB
filehandle_limit=100	#num
disk_limit=204800	#KB
processnum_limit=2	#num

#define  usage
def usage():
    print "usage: %s -p [ process PID ] <option> <interval check time(sec)>" %(sys.argv[0])
    print "       %s -n [ process name ] <option> <interval check time(sec)>\n" %(sys.argv[0])
    print "<option>: -cpu check cpu usage satatus"
    print "<option>: -mem check memory usage satatus"
    print "<option>: -file check file handle usage satatus"
    print "<option>: -disk check disk usage satatus"
    print "<option>: -all check all resource usage satatus\n"
    print "ex. % -n hosteye -a 60"
    print "check hosteye process all resouce status every 60 sec."
    sys.exit (1)
try:
    scriptname=sys.argv[0]
    parm=sys.argv[1]
    parm_content=sys.argv[2]
    option=sys.argv[3]
except Exception,e:
    usage()
    #	print "parmeter error:",e

#basic info
def get_pid():
    try:
	if parm == "-n":
	    cmd='ps -ef | grep ' + parm_content + '$| grep -v grep |grep -v ' + scriptname + '|awk {\'print $2\'}'
	    (status,output)=commands.getstatusoutput(cmd) 
	    if len(output) != 0:
		pidlist=output
	    else:
		print '\033[1;31;40m',"can not find process name: %s \n" %(parm_content),'\033[0m'
		usage()
	if parm == "-p":
	    cmd='ps -ef | grep ' + parm_content + '$|grep -v grep | wc -l '
	    (status,output)=commands.getstatusoutput(cmd)
	    if int(output) != 0:
		pidlist=parm_content 
	    else:
		print '\033[1;31;40m',"can not find process pid: %s\n" %(parm_content),'\033[0m'
		usage()
	return pidlist
    except Exception ,e:
	usage()

#memory check
def mem_usage_check():
    vm_total=0    
    rss_total=0
    getpid=get_pid()
    for pid in re.split('\n',getpid):
	filepath="/proc/" + pid + "/status"
	try:
	    f=open(filepath,'r')
	except Exception,e:
	    print "open file %s failed. " %filepath,"detail:",e
	    sys.exit(-1)
	try:
	    for line in f.readlines():
		if line.find('VmSize') != -1:
		    vm=re.split('\s+',line)[1]
		    vm_total=vm_total + int(vm)
		    print "pid %s Vm(Virtual memory size) size: %s KB." %(pid,vm)
		if line.find('VmRSS') != -1:
		    rss=re.split('\s+',line)[1]
		    rss_total=rss_total + int(rss)
		    print "pid %s RSS(Resident set size) size: %s KB." %(pid,rss)
	except Exception,e:
	    print "read file %s failed. " %filepath,"detail:",e
	    sys.exit(-1)
	finally:
	    f.close()
    print "\n%s total Vm(Virtual memory size) size: %s KB." %(parm_content,vm_total)
    print "%s total RSS(Resident set size) size: %s KB." %(parm_content,rss_total)
    if int(vm_total) >= mem_limit:
	logging.error("Vm size: %s big than expect limie: %s KB",vm_total, mem_limit)
    else:
	logging.info("Vm size: %s KB",vm_total)
    if int(rss_total) >= mem_limit:
	logging.error("RSS size: %s KB big than expect limie: %s KB",rss_total, mem_limit)
    else:
	logging.info("RSS size: %s KB",rss_total)

#CPU check
def cpu_usage_check():
    pid=get_pid()
    pidlist=re.split('\n',pid)
    pids=[]
    for pid in pidlist:
	pids.append(pid)
	pids.append(',')
    pids.pop()	#del last ","
    pidstr=''.join(pids)
    cmd='top -b -p ' + pidstr + ' -n 1 |tail -n ' + str((len(pidlist) + 1)) + '|head -n ' + str(len(pidlist))	#remember: top need use -b 
    output=commands.getoutput(cmd)
    lines=[]
    try:
	for line in re.split('\n',output.strip('\n')):
	    words=[]
	    for word in re.split('\s+',line):
		words.append(word)
	    lines.append(words)
	cpu_total=0.0
	for cpu in lines:
	    cpu_total = cpu_total + float(cpu[8])
	    print "pid %s cpu usage: %s" %(cpu[0],cpu[8])
	    logging.info("pid %s cpu usage: %s" ,cpu[0],cpu[8])
	print "Total cpu usage: %s" %cpu_total
    except Exception,e:
	print e
	logging.error ("error:%s",e)
    if cpu_total <= cpu_limit:
	logging.info("Total CPU usage: %s ",cpu_total)
    else:
	logging.error("Total CPU usage : %s big than expect limie: %s ",cpu_total, cpu_limit)

#disk usage check
def disk_usage_check():
    size=0L
    dir="/opt/hosteye/"
#    for root,dirs,files in os.walk(dir):
#	size +=sum([os.path.getsize(os.path.join(root,name)) for name in files])
#	print size/1024
    cmd='du -k '+ dir + '|tail -n 1'
    (status,output)=commands.getstatusoutput(cmd)
    disk_status=[]
    for item in re.split("\s+",output):
	disk_status.append(item)
    disk_usage=int(disk_status[0])
    if int(disk_usage) > disk_limit:
	print "Disk usage check failed! now: %s KB expected: %s KB" %(disk_usage, disk_limit)
	logging.error("Disk usage size %s KB big than expected: %s KB" ,disk_usage, disk_limit)
    else:
	print "Disk usage check OK: %s KB" %(disk_usage)
	logging.info("Disk usage check OK: %s KB" ,disk_usage)
	
	
#file open number check
def file_handle_check():
    getpid=get_pid()
    file_handle={}
    for pid in re.split("\s+",getpid):
        cmd='/usr/sbin/lsof -p ' + pid + ' |wc -l'
	(status,output)=commands.getstatusoutput(cmd)
	file_handle[pid]=int(output);
    for key in file_handle.keys():
	print "%s  file handle: %s" %(key,file_handle[key])
    fopen_sum=sum(file_handle.values())
    print "total file handle: %s" %(fopen_sum)
    if fopen_sum >= filehandle_limit:
        logging.error("total file handle: %s big than expect limit: %s",fopen_sum,filehandle_limit)
    else:
        logging.info("total file handle: %s ",fopen_sum)

#process status check
def service_status_check():
    getpid=get_pid()
    pidlist=[]
    for pid in re.split("\s+",getpid):
	pidlist.append(pid)
    if len(pidlist) != processnum_limit:
	print "%s process abnormally, pid:%s" %(parm_content,getpid)
        logging.error("process number abnormally pid: %s (total: %s ),expect pid number:%s",pidlist,len(pidlist),processnum_limit)
    else:
	print "%s process OK, pid:\n%s" %(parm_content,getpid)
        logging.info("process number OK: %s ",len(pidlist))

def loop_logic(func):
    if len(sys.argv) == 5:
	while 1:
	    func()
	    time.sleep(int(sys.argv[4]))
    else:
	func()

def main():
    try:
	service_status_check()
	if option == "-cpu":
	    loop_logic(cpu_usage_check)
	if option == "-mem":
	    loop_logic(mem_usage_check)
	if option == "-file":
	    loop_logic(file_handle_check())
	if option == "-disk":
	    loop_logic(disk_usage_check())
	if option == "-all":
	    if len(sys.argv) == 5:
		while 1:
		    cpu_usage_check()
		    mem_usage_check()
		    file_handle_check()
		    disk_usage_check()
		    time.sleep(int(sys.argv[4]))
	    else:
		cpu_usage_check()
		mem_usage_check()
		file_handle_check()
		disk_usage_check()
    except Exception,e:
	print e
	logging.error("error: %s", e)

if __name__=='__main__':
    main()

