#!/usr/bin/env python
import operator,os,sys

try:
    if len(sys.argv) != 3:
	print "usage: %s <file1> <file2>" %(sys.argv[0])
	sys.exit(0)

    if os.path.isfile(sys.argv[1]) and os.path.isfile(sys.argv[2]):
	f1=open(sys.argv[1],'r')
        f2=open(sys.argv[2],'r')
	f1_name='%s.%s' %(sys.argv[1],'only')
	f2_name='%s.%s' %(sys.argv[2],'only')
	f1_f2_name='%s_%s.%s' %(sys.argv[1],sys.argv[2],'all')
	f1_only=open(f1_name,'w')
	f2_only=open(f2_name,'w')
	f1_f2=open(f1_f2_name,'w')
    else:
	print "file not exist "
	sys.exit(0)

    line1=f1.readlines()
    line2=f2.readlines()

    dict1={}
    dict2={}
except Exception, e:
    print 'file define Error:',e

try :
    for tmp1 in line1:
	tmp1=tmp1.strip('\n')
	dict1[tmp1] = 0
    
    for tmp2 in line2:
	tmp2=tmp2.strip('\n')
	dict2[tmp2] = 0
except Exception,e:
    print 'dict define Error:',e

try :
    for tmp1 in dict1:
	for tmp2 in dict2:
	    if operator.eq(tmp2,tmp1):
		dict1[tmp1]=1
		dict2[tmp2]=1

    for key1 in dict1:
	if dict1[key1] == 0:
	    f1_only.write(key1+'\n')

    for key2 in dict2:
	if dict2[key2] == 0:
	    f2_only.write(key2+'\n')
	else:
	    f1_f2.write(key2+'\n')

    print "%s particular: %s" %(sys.argv[1],f1_name)
    print "%s particular: %s" %(sys.argv[2],f2_name)
    print "%s and %s common: %s" %(sys.argv[1],sys.argv[2],f1_f2_name)
    f1.close
    f2.close

except Exception,e:
    print 'diff calculate Error:',e


