#!/usr/bin/env python

import sys,os,ConfigParser
import re,commands

#check ENV
#===program check===
def command_check(cmdline):
    cmd = 'whereis ' + cmdline
    output = commands.getoutput(cmd)
    if len(output) <= len(cmdline) + 2:
	print "Check command %s ... failed ... quit" %cmdline
	sys.exit(1)
    else:
	print "Check command %s ... OK "%cmdline
	
#===config file check===
def config_check():
    str = '''#tcpreplay config.
# disable  means single parameter
# none  means str parameter
# 0  means number parameter
#other format parameter please follow comments
#
[tcpprep]
split-mode=port         # auto/cidr/regex/port/mac
auto-str=bridge         #bridge/router/client/server/first
cidr-str= 172.22.64.2/24
regex-str= test
mac-str= 70:E2:84:0B:F3:DA
cachefile= tcpreplay.cache
port= none
pcap= test.pcap

[tcprewrite]
tcprewrite-status = enable      #enable/disable tcprewrite
portmap= none
seed= 0
pnat= none              #Rewrite IPv4/v6 addresses using pseudo-NAT
srcipmap= none          #Rewrite source IPv4/v6 addresses using pseudo-NAT
stipmap= none          #Rewrite destination IPv4/v6 addresses using pseudo-NAT
endpoints= none         #Rewrite IP addresses to be between two endpoints
skipbroadcast= disable         #Skip rewriting broadcast/multicast IPv4/v6 addresses
fixcsum= disable               #Force recalculation of IPv4/TCP/UDP header checksums
mtu= 0               #Override default MTU length (1500 bytes)
mtu-trunc= disable             #Truncate packets larger then specified MTU
efcs= disable                 #Remove Ethernet checksums (FCS) from end of frames
ttl= none               #Modify the IPv4/v6 TTL/Hop Limit
tos= 0               #Set the IPv4 TOS/DiffServ/ECN byte
tclass= 0            #Set the IPv6 Traffic Class byte
fixlen= none            #Pad or truncate packet data to match header length
skipl2broadcast= disable       #Skip rewriting broadcast/multicast Layer 2 addresses
dlt= none               #Override output DLT encapsulation
enet-dmac= none         #Override destination ethernet MAC addresses
enet-smac= none         #Override source ethernet MAC addresses
endpoint= 10.107.244.140:10.107.244.147  #Rewrite IP addresses to be between two endpoints
cachefile= none         #default use tcpprep cachefile settings.
infile= none    #default use tcpprep pcap settings.
outfile= tcprewrite.pcap        #default outfile is tcprewrite.pcap

[tcpreplay]
quiet= disable                 #Quiet mode
timer= none             #Select packet timing mode: select, ioport, gtod, nano
maxsleep= 0          #Sleep for no more then X milliseconds between packets
verbose= disable              #Print decoded packets via tcpdump to STDOUT
decode= none            #Arguments passed to tcpdump decoder
preload-pcap= disable         #Preloads packets into RAM before sending
cachefile= none         #Split traffic via a tcpprep cache file
dualfile= disable             #Replay two files at a time from a network tap
intf1= none             #Client to server/RX/primary traffic output interface
intf2= none             #Server to client/TX/secondary traffic output interface
listnics= disable             #List available network interfaces and exit
loop= 0              #Loop through the capture file X times
loopdelay-ms= 0      #Delay between loops in milliseconds
pktlen= disable               #Override the snaplen and use the actual packet len
limit= 0             #Limit the number of packets to send
duration= 0          #Limit the number of seconds to send
multiplier= none        #Modify replay speed to a given multiple
pps= 0               #Replay packets at a given packets/sec
mbps= none              #Replay packets at a given Mbps
topspeed= enable             #Replay packets as fast as possible
oneatatime= disable           #Replay one packet at a time for each user input
pps-multi= 0         #Number of packets to send for each time interval
unique-ip= disable            #Modify IP addresses each loop iteration to generate unique flows
no-flow-stats= disable         #Suppress printing and tracking flow count, rates and expirations
flow-expiry= none       #Number of inactive seconds before a flow is considered expired
pid= disable                  #Print the PID of tcpreplay at startup
quick-tx= disable             #Write packets directly to an interface via Quick_TX module
stats= 0             #Print statistics every X seconds
pcap_file = test.pcap   #default file is tcpprep pcap file'''

    if not os.path.exists("./tcpreplay.conf"):
	with open('./tcpreplay.conf','w') as f:
	    f.writelines(str)
	print "Default tcpreplay.conf not exist, create default config file ... done"

#get config
def getconf(section,key):
    config = ConfigParser.ConfigParser()
    conf_path = "tcpreplay.conf"
    config.read(conf_path)
    return re.split('\s+',config.get(section,key))[0]

#tcpprep recover
#tcpprep --auto=client --cachefile=/root/tcpreplay/test.pcap --pcap=/root/tcpreplay/icmp.pcap
#def tcpprep_conf_parser():
def err_log(str):
    print "%s parameter error" %str
    sys.exit(1)

def tcpprep_run():
    #parameter have value
    tcpprep_para={}
    tcpprep_no_para=[]
    split_mode = getconf("tcpprep","split-mode")       # auto/cidr/regex/port/mac
    cachefile = getconf("tcpprep","cachefile")
    pcap=getconf("tcpprep","pcap")
    if split_mode == 'auto':
	auto_value_list = ("bridge","router","client","server","first")
	auto_value = getconf("tcpprep","auto-str")       #bridge/router/client/server/first
	print "auto :",auto_value
	if auto_value in auto_value_list:
	    tcpprep_para[split_mode] = auto_value
	else:
	    print "auto parameter error"
	    sys.exit(1)
    if split_mode == "cidr":
	tcpprep_para[split_mode] = getconf("tcpprep","cidr-str")
    if split_mode == "regex":
	tcpprep_para[split_mode] = getconf("tcpprep","regex-str")
    if split_mode == "mac":
	tcpprep_para[split_mode] = getconf("tcpprep","mac-str")

    if cachefile == "" or cachefile == "none":
	cachefile = "tcpreplay.cache"
    else:
	cachefile = getconf("tcpprep","cachefile")
    tcpprep_para["cachefile"] = cachefile

    pcap = getconf("tcpprep","pcap")
    if os.path.isfile(pcap):
	tcpprep_para["pcap"] = pcap
    else:
	print "Can not find pcap file:", pcap
	sys.exit(1)

    #parameter no value
    if split_mode == "port":
	tcpprep_no_para.append("port")
 
    tcpprep_str = ''
    for item,value in tcpprep_para.items():
	tcpprep_group = "--%s=%s " %(item,value)
	tcpprep_str = tcpprep_str + tcpprep_group
    #print "with value parameter:", tcpprep_str
    for key in tcpprep_no_para:
	tcpprep_group = "--%s " %key
	tcpprep_str = tcpprep_str + tcpprep_group
    #print "without value parameter:", tcpprep_str
    cmd = "tcpprep " + tcpprep_str
    #print "run cmd: ",cmd
    (status,output) = commands.getstatusoutput(cmd)
    if status != "0":
	print "tcpprep execute success:",status
    else:
	print "tcpprep execute failed:",status
    print output

def para_attach(dict,section,str):
    key = getconf(section,str)
    if key != "none" and key != "0":
	dict[str] = key
    return dict
def nopara_attach(list,section,str):
    key = getconf(section,str)
    if key == "enable":
	list.append(str)
    elif key == "disable":
	pass
    else:
	err_log(str)
    return list
	
#tcprewrite recover
#tcprewrite --endpoint=10.107.244.140:10.107.244.147 --cachefile=test.pcap --infile=icmp.pcap --outfile=my.pcap
def tcprewrite_run():
    tcprewrite_status = getconf("tcprewrite","tcprewrite-status")     #enable/disable tcprewrite
    if tcprewrite_status == "enable":
	tcprewrite_para={}
	tcprewrite_no_para=[]
	#without para
	nopara_attach(tcprewrite_no_para, "tcprewrite", "efcs")		#Remove Ethernet checksums (FCS) from end of frames
	nopara_attach(tcprewrite_no_para, "tcprewrite", "mtu-trunc")		#Truncate packets larger then specified MTU
	nopara_attach(tcprewrite_no_para, "tcprewrite", "fixcsum")		#Force recalculation of IPv4/TCP/UDP header checksums
	nopara_attach(tcprewrite_no_para, "tcprewrite", "skipbroadcast")	#Skip rewriting broadcast/multicast IPv4/v6 addresses
	nopara_attach(tcprewrite_no_para, "tcprewrite", "skipl2broadcast")	#Skip rewriting broadcast/multicast Layer 2 addresses

	#with para
	para_attach(tcprewrite_para, "tcprewrite", "portmap")
	para_attach(tcprewrite_para, "tcprewrite", "seed")
	para_attach(tcprewrite_para, "tcprewrite", "pnat")            #Rewrite IPv4/v6 addresses using pseudo-NAT
	para_attach(tcprewrite_para, "tcprewrite", "srcipmap")         #Rewrite source IPv4/v6 addresses using pseudo-NAT
	para_attach(tcprewrite_para, "tcprewrite", "stipmap")        #Rewrite destination IPv4/v6 addresses using pseudo-NAT
	para_attach(tcprewrite_para, "tcprewrite", "endpoints")        #Rewrite IP addresses to be between two endpoints
	para_attach(tcprewrite_para, "tcprewrite", "mtu")              #Override default MTU length (1500 bytes)
	para_attach(tcprewrite_para, "tcprewrite", "ttl")              #Modify the IPv4/v6 TTL/Hop Limit
	para_attach(tcprewrite_para, "tcprewrite", "tos")              #Set the IPv4 TOS/DiffServ/ECN byte
	para_attach(tcprewrite_para, "tcprewrite", "tclass")           #Set the IPv6 Traffic Class byte
	para_attach(tcprewrite_para, "tcprewrite", "fixlen")           #Pad or truncate packet data to match header length
	para_attach(tcprewrite_para, "tcprewrite", "dlt")              #Override output DLT encapsulation
	para_attach(tcprewrite_para, "tcprewrite",  "enet-dmac")        #Override destination ethernet MAC addresses
	para_attach(tcprewrite_para, "tcprewrite", "enet-smac")        #Override source ethernet MAC addresses
	para_attach(tcprewrite_para, "tcprewrite", "endpoint") #Rewrite IP addresses to be between two endpoints

	#default settings
	cachefile = getconf("tcprewrite", "cachefile")	    #default use tcpprep cachefile settings.
	infile = getconf("tcprewrite", "infile")	    #default use tcpprep pcap settings.
	outfile =  getconf("tcprewrite", "outfile")	    #default outfile is tcprewrite.pcap
	if cachefile == "none":
	    cachefile = getconf("tcpprep", "cachefile")
	if infile == "none":
	    infile = getconf("tcpprep","pcap")
	if outfile == "none":
	    outfile = "tcprewrite.pcap"
	tcprewrite_default = "--cachefile=%s --infile=%s --outfile=%s " %(cachefile, infile, outfile)

	#combine commands
	tcprewrite_str = ''
	for item,value in tcprewrite_para.items():
	    tcprewrite_group = "--%s=%s " %(item,value)
	    tcprewrite_str = tcprewrite_str + tcprewrite_group
#	print "with value parameter:", tcprewrite_str
	for key in tcprewrite_no_para:
	    tcprewrite_group = "--%s " %key
	    tcprewrite_str = tcprewrite_str + tcprewrite_group
#	print "without value parameter:", tcprewrite_str

	cmd = "tcprewrite " + tcprewrite_str + tcprewrite_default 
#	print "run cmd: ",cmd
	(status,output) = commands.getstatusoutput(cmd)
	if status != "0":
	    print "tcprewrite execute success:",status
	else:
	    print "tcprewrite execute failed:",status
	print output
    else:
	print "tcprewrite was set disabled, pass this step ..."
	pass

#tcpreplay recover
#tcpreplay --intf1=eth0 --intf2=eth0 --cachefile=test.pcap my.pcap
def tcpreplay_run():
    tcpreplay_para={}
    tcpreplay_no_para=[]
    #default settings
    cachefile=getconf("tcpreplay","cachefile")        #Split traffic via a tcpprep cache file
    intf1=getconf("tcpreplay","intf1")            #Client to server/RX/primary traffic output interface
    intf2=getconf("tcpreplay","intf2")            #Server to client/TX/secondary traffic output interface
    pcap_file = getconf("tcpreplay","pcap_file")
    if cachefile == "none":
	cachefile = getconf("tcpprep","cachefile")
    if intf1 == "none":
	intf1 = "eth0"
    if intf2 == "none":
	intf2 = "eth0"
    if pcap_file == "none":
	pcap_file = getconf("tcpreplay", "pcap_file")
    tcpreplay_default = "--cachefile=%s --intf1=%s --intf2=%s %s" %(cachefile, intf1, intf2, pcap_file)

    #para setings
    para_attach(tcpreplay_para, "tcpreplay","timer") #Select packet timing mode: select, ioport, gtod, nano
    para_attach(tcpreplay_para, "tcpreplay","maxsleep") #Sleep for no more then X milliseconds between packets
    para_attach(tcpreplay_para, "tcpreplay","decode") #Arguments passed to tcpdump decoder
    para_attach(tcpreplay_para, "tcpreplay","loop") #Loop through the capture file X times
    para_attach(tcpreplay_para, "tcpreplay","loopdelay-ms")     #Delay between loops in milliseconds
    para_attach(tcpreplay_para, "tcpreplay","limit") #Limit the number of packets to send
    para_attach(tcpreplay_para, "tcpreplay","duration") #Limit the number of seconds to send
    para_attach(tcpreplay_para, "tcpreplay","multiplier") #Modify replay speed to a given multiple
    para_attach(tcpreplay_para, "tcpreplay","pps") #Replay packets at a given packets/sec
    para_attach(tcpreplay_para, "tcpreplay","mbps") #Replay packets at a given Mbps
    para_attach(tcpreplay_para, "tcpreplay","pps-multi")        #Number of packets to send for each time interval
    para_attach(tcpreplay_para, "tcpreplay","flow-expiry")       #Number of inactive seconds before a flow is considered expired
    para_attach(tcpreplay_para, "tcpreplay","stats") #Print statistics every X seconds

    #no_para settings
    nopara_attach(tcpreplay_no_para, "tcpreplay", "quiet")#Quiet mode
    nopara_attach(tcpreplay_no_para, "tcpreplay", "verbose")		#Print decoded packets via tcpdump to STDOUT
    nopara_attach(tcpreplay_no_para, "tcpreplay", "preload-pcap")	#Preloads packets into RAM before sending
    nopara_attach(tcpreplay_no_para, "tcpreplay", "dualfile")		#Replay two files at a time from a network tap
    nopara_attach(tcpreplay_no_para, "tcpreplay", "listnics")		#List available network interfaces and exit
    nopara_attach(tcpreplay_no_para, "tcpreplay", "pktlen")		#Override the snaplen and use the actual packet len
    nopara_attach(tcpreplay_no_para, "tcpreplay", "topspeed")		#Replay packets as fast as possible
    nopara_attach(tcpreplay_no_para, "tcpreplay", "oneatatime")		#Replay one packet at a time for each user input
    nopara_attach(tcpreplay_no_para, "tcpreplay", "unique-ip")		#Modify IP addresses each loop iteration to generate unique flows
    nopara_attach(tcpreplay_no_para, "tcpreplay", "no-flow-stats")	#Suppress printing and tracking flow count, rates and expirations
    nopara_attach(tcpreplay_no_para, "tcpreplay", "pid")		#Print the PID of tcpreplay at startup
    nopara_attach(tcpreplay_no_para, "tcpreplay", "quick-tx")		#Write packets directly to an interface via Quick_TX module

    #combine commands
    tcpreplay_str = ''
    for item,value in tcpreplay_para.items():
	tcpreplay_group = "--%s=%s " %(item,value)
	tcpreplay_str = tcpreplay_str + tcpreplay_group
#    print "with value parameter:", tcpreplay_str
    for key in tcpreplay_no_para:
	tcpreplay_group = "--%s " %key
	tcpreplay_str = tcpreplay_str + tcpreplay_group
#    print "without value parameter:", tcpreplay_str

    cmd = "tcpreplay " + tcpreplay_str + tcpreplay_default
#    print "run cmd: ",cmd
    (status,output) = commands.getstatusoutput(cmd)
    if status != "0":
	print "tcpreplay execute success:",status
    else:
	print "tcpreplay execute failed:",status
    print output


if __name__=="__main__":
    command_check("tcpprep")
    command_check("tcprewrite")
    command_check("tcpreplay")
    config_check()
    tcpprep_run()
    tcprewrite_run()
    tcpreplay_run()

