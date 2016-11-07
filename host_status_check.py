#!/usr/bin/env python
#check machine status by hostname.

import re,subprocess,os,sys
import paramiko


def usage():
    if len(sys.argv) != 3:
	print "usage: %s -f <machine_list_file>" %(sys.argv[0])
	print "       %s -n <hostname>" %(sys.argv[0])
	sys.exit(0)

def write_file(result):
    log.write(result)
    log.flush()

def ping_check(hostname):
	cmd="ping -c 2 -w 2 " + hostname
	p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
	out=p.stdout.read()
	lossall=re.compile('100% packet loss')
	unknow=re.compile('unknown host')
	if len(lossall.findall(out)) != 0:
	    print hostname + "\t disconnect \n"
	    return ("network status: disconnect")
	elif len(unknow.findall(out)) != 0:
	    print hostname + "\t unknow hostname\n"
	    return ("network status: DNS resolve error")
	else:
	    print hostname + "\t alive \n"
	    return ("network status: alive")

def ssh_check(hostname):
    port=22
    username="root"
    password="isys.INIT@2014"

    cmd1="ps -ef | grep hosteye |wc -l"
    cmd2="find /noah/modules/ -name \"hosteye\""

    paramiko.util.log_to_file('param.log')
    #connection test
    try:
	s=paramiko.SSHClient()
        s.load_system_host_keys()
	s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(hostname,port,username,password)
    except Exception,e:
        print "SSH connection error: %s", e
	return str(e)

    #pramgram test
    try:
        stdin,stdout,stderr=s.exec_command(cmd1,timeout=20.0)
        cmd1_result=stdout.read().strip('\n')
        print "cmd1:%s" %(cmd1_result)
        if cmd1_result == '1':
            print "hosteye paramgram no run"
            cmd1_str="threading: stop"
        elif cmd1_result == '5':
            print "hosteye paramgram is running"
            cmd1_str="threading: run"
        else:
            print "hosteye paramgram number error"
            cmd1_str="threading: error"
    except Exception,e:
        print "command execute error, %s",e
	cmd1_str="Exception: ps command execute timeout or error"

    #install status test
    try:
        stdin,stdout,stderr=s.exec_command(cmd2,timeout=20.0)
        cmd2_result=stdout.read().strip('\n')
        print "cmd2:%s" %(cmd2_result)
        tmp=cmd2_result.split("/")[:-1]
        tmp.append("..")
        tmp.append("NOAH")
        tmp.append("control")
        control_cmd='/'.join(tmp) + ' ' + "status"
        if cmd2_result == "":
            print "hosteye not install"
            cmd2_str="install: NO"
	else:
            print "hosteye has installed"
            cmd2_str="install: YES"
    except Exception,e:
        print "command execute error, %s",e
	cmd2_str="Exception: find command execute timeout or error"

    #running status test
    try:
        stdin,stdout,stderr=s.exec_command(control_cmd,timeout=20.0)
        cmd3_result=stdout.read().strip('\n')
        print "cmd3:%s" %(cmd3_result)
        if cmd3_result == 'Running':
            print "hosteye status is running"
            cmd3_str="status:running"
        else:
            print "hosteye status is stop"
            cmd3_str="status:stop"
    except Exception,e:
        print "command execute error, %s",e
	cmd3_str="Exception: hosteye status command execute timeout or error"

    seq=(cmd1_str,cmd2_str,cmd3_str,)
    s.close()
    return (' ; '.join(seq))

def main():
    global log
    usage()  
    log_name=sys.argv[0] + ".log"
    log=open(log_name,'a')
    f=open(sys.argv[2],'r')
    lines=f.readlines()
    for line in lines:
	hostname=line.strip('\n')
	ping_result=ping_check(hostname)
	if "disconnect" in ping_result or "DNS result error" in ping_result:
	    tmp=(hostname,ping_result)
	    write_file(ping_result)
	if "alive" in ping_result:
#	    write_file(hostname,ping_result)
	    ssh_result=ssh_check(hostname)
	    tmp=(hostname,ping_result,ssh_result,'\n')
	    final_result=' | '.join(tmp)
	    write_file(final_result)

    f.close()
    log.close()

if __name__ =='__main__':
    main()

#    (status,output)=commands.getstatusoutput(cmd)
#    print "status: %s" %(status)
#    print "output: %s" %(output)
#    sys.exit(0)
