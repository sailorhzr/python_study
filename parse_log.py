#!/usr/bin/env python
#create by sailor.H for DPDK test. summary pps and bbs in log

import time,sys,re

default_ds_path='/home/work/mirror-ds/output/log/ds.log'

try:
    if sys.argv[1] == '-c':
	f = open(default_ds_path,"w")
	f.truncate()
	sys.exit(1)
except Exception,e:
    pass

if int(len(sys.argv)) == 2:
    file=sys.argv[1]
else:
    file=default_ds_path

try:
    f=open(file)
except:
    print "open failed"
    exit (-1)

worker0_pps=[]
worker1_pps=[]
worker2_pps=[]
worker3_pps=[]
worker0_bbs=[]
worker1_bbs=[]
worker2_bbs=[]
worker3_bbs=[]

def cal(workname):
    if line.find(workname) != -1:
	str=re.split('\s+',line)
	pps_str=str[13][:-1]    #remove ,
	bbs_str=str[15]
	if workname.find('0') != -1:
	    worker_pps=worker0_pps
	    worker_bbs=worker0_bbs
	if workname.find('1') != -1:
	    worker_pps=worker1_pps
	    worker_bbs=worker1_bbs
	if workname.find('2') != -1:
	    worker_pps=worker2_pps
	    worker_bbs=worker2_bbs
	if workname.find('3') != -1:
	    worker_pps=worker3_pps
	    worker_bbs=worker3_bbs
	worker_pps.append(int(pps_str))
	worker_bbs.append(int(bbs_str))
#	print pps_str
#	print bbs_str

try:
    line=f.readline()
    while line:
	cal('worker 0')
	cal('worker 1')
	cal('worker 2')
	cal('worker 3')
	line=f.readline()
except:
    print "read file failed"

finally:
    f.close

print "worker0 pps: %s bps: %s" %(sum(worker0_pps),sum(worker0_bbs))
print "worker1 pps: %s bps: %s" %(sum(worker1_pps),sum(worker1_bbs))
print "worker2 pps: %s bps: %s" %(sum(worker2_pps),sum(worker2_bbs))
print "worker3 pps: %s bps: %s" %(sum(worker3_pps),sum(worker3_bbs))
total_pps=sum(worker0_pps) + sum(worker1_pps) + sum(worker2_pps) + sum(worker3_pps)
total_bbs=sum(worker0_bbs) + sum(worker1_bbs) + sum(worker2_bbs) + sum(worker3_bbs)
print "total   pps: %s bps: %s" %(total_pps,total_bbs)

print "\n============================================\n"
print "usage: %s [-c] [ds log path] " %(sys.argv[0])
print "Ex: %s -c              #clean log" %(sys.argv[0])
print "Ex: %s /home/work/mirror-ds/output/log/ds.log       #calculate log" %(sys.argv[0])
print "default log path: %s" %(default_ds_path)


