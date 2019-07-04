import socket
import csv
import sys
import argparse
import os
import get_ips
import re

def hostname_resolves(hostname,debug,progress):
    try:
	if args.debug and not progress:
            	toDebug("Try resolve->"+str(hostname))
        res=socket.gethostbyname(hostname.replace('www.',''))
	if args.debug and not progress:
            	toDebug("Resolved->"+str(res))
        return res
    except socket.error:
	if args.debug and not progress:
        	toDebug("Error resolv->"+str(hostname))
        return 0

def toDebug(element):
	try:
		print(element)
	except:
		print element

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some contiries.')
    parser.add_argument('--country', metavar='', type=str, nargs='+', help='contiries (default: all)')
    parser.add_argument('--file', help='file to write (default: stdout)')
    parser.add_argument('--debug', help='debug information (default: false)')
    parser.add_argument('--infocount', help='information count work (default: false)')
    parser.add_argument('--inforesult', help='information result only (default: false)')
    parser.add_argument('--usetemp', help='use temp list,duplicate exclude, before write to file (default: false)')
    parser.add_argument('--progressbar', help='show progress bar need progressbar module [pip install progressbar] (default: false)')
    

    args = parser.parse_args()
    if args.progressbar:
	import progressbar
    if args.file:
        out = open(args.file,'w')
    else:
        out = sys.stdout

    filename = 'acs_url.csv'
    result=[]
    with open(filename, 'rb') as csvFile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='"')
        if args.country:
            reader = filter( lambda x: x[2] in args.country, reader)
	cnt=0
	cnt_wrong=0
	i=0
	if args.progressbar:
		bar = progressbar.ProgressBar(maxval=len(reader), \
    			widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
		bar.start()
        for row in reader:
            wrongMark=False
            ret = get_ips.get_ips(row)
	    if args.debug and not args.progressbar:
            	toDebug(ret)
	    if not len(ret[3]):
		rs=hostname_resolves(ret[0],args.debug,args.progressbar)
		if rs:
			ret[3]=[rs]
	    if args.debug and not args.progressbar:
            	toDebug(ret[3])
	    	toDebug(" len->"+str(len(ret[3])))
	    if len(ret[3])>15:
		if args.debug and not args.progressbar:
			toDebug(ret[3])
		wrongMark=True
	    	cnt_wrong=cnt_wrong+ len(ret[3])
	    if args.progressbar:
	    	bar.update(i+1)
	    cnt=cnt+len(ret[3])

            if len(ret[3]):
    		if re.match(r"^\[\'(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\'\]$",str(ret[3])):
			ip=str(ret[3])[2:-2]			
			if not args.usetemp:
    				out.writelines([ip + os.linesep])
			else:
				if not ip in result:
					result.append(ip)
				else:
					cnt=cnt-1
			if wrongMark:
				cnt_wrong=cnt_wrong-1
    		elif re.match(r"^\[\'.*\'\]$",str(ret[3])):
				ips=str(ret[3])[2:-2].split(',')
				for ip in ips:
					ip=re.sub("[^0123456789\.]","",ip)
					if re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",ip):
						if not args.usetemp:
							out.writelines([ip + os.linesep ])
						else:
							if not ip in result:
								result.append(ip)
							else:
								cnt=cnt-1
						if wrongMark:
							cnt_wrong=cnt_wrong-1
	    i=i+1
	if args.progressbar:
		bar.finish()
    if args.usetemp:
	    out.writelines([ip + os.linesep for ip in result])
    if args.debug or args.infocount or args.inforesult:
	    if not args.inforesult:
		    toDebug("count source rows->"+str(len(reader)))
		    toDebug("count work->"+str(cnt))
		    toDebug("count wrong->"+str(cnt_wrong))
		    toDebug("count work minus count wrong->"+str(cnt-cnt_wrong))
	    if args.usetemp:
		    if not args.inforesult:
		    	toDebug("Count temp->"+str(len(result)))
		    if args.debug:
		    	toDebug(result)
		    if len(result)==cnt-cnt_wrong:
		    	toDebug("all fine equals!!!")
    if args.file:
	out.close()
	if args.debug or args.infocount or args.inforesult:
		if sum(1 for line in open(args.file,'r'))==cnt-cnt_wrong:
			toDebug("all fine write to file!!!")
