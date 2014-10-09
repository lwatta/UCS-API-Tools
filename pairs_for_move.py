#!/usr/bin/python


# Purpose: Automate Kernel and OVS commands
#
# Outline
#	Open file with pairs of hosts
#	Create service disable command
#	create live migration commands 
#	Raise alarm for any SP that is not associated.



# Import crap
import simplejson as json
import time
import datetime
import sys
import getopt
import getpass
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(description='Script to commands for OVS/Kernel Remediation. If only one host is present in the inputfile the script will create live-migration commands without a target. To have the script create live migration commands with targets have the input file be a pairing of source target')
parser.add_argument('-i', dest='inputfile', action='store',
                    help='Input file of hosts. Sinlge host list or pairs.')
parser.add_argument('-o', dest='outputfile', action='store',
                    help='Output file for commands for nova service-disable, live-migration, service-enable')

args = parser.parse_args()
# open output file 
if not args.outputfile:
	output = open('./commandlist.txt', 'w')
else:
	output = open(args.outputfile, 'w')

if not args.inputfile:
	print "no inputfile"
	sys.exit(0)
# open pairs file and start creating commands
output.write("--------------------   Disable Service ---------------------------")
for templine in open (args.inputfile).readlines():
	temp = templine.split()
	source = temp[0]
	

# parse through file and create nova command to disable on column1
	outputlist = "nova service-disable --reason \"Down for OVS\/Kernel Upgrade\" " +source +" nova-compute\n"
	print outputlist
	output.write(outputlist)

# parse through file an create live migration command column1 to column2
output.write("--------------------   Live Migration  ---------------------------")
for templine in open (args.inputfile).readlines():
	temp = templine.split()
	source = temp[0]
	if len(temp) == 1:
	# get list of VMs based egrep -v 'SHUTOFF|SUSPENDED|PAUSED|ERROR'
		outputlist = "nova list --all-tenants --host=" +source +" |depipe | grep -v ID | grep ACTIVE |awk \'{print \"nova live-migration \"$1\" "  +"\"}\' \n"
		
	elif len(temp) == 2:
		target = temp[1]
		outputlist = "nova list --all-tenants --host=" +source +" |depipe | grep -v ID | grep ACTIVE |awk \'{print \"nova live-migration \"$1\" " +target +"\"\\' \n"

	print outputlist
	output.write(outputlist)
	


# parse through file and create nova command to enable on column1
output.write("--------------------   Enable Service ---------------------------")
for templine in open (args.inputfile).readlines():
	temp = templine.split()
	source = temp[0]

# parse through file and create nova command to disable on column1
	outputlist = "nova service-enable " +source +" nova-compute\n"
	print outputlist
	output.write(outputlist)
	



#for item in listoflists:
#        stringconvert= ",".join(item)
#        stringconvert= stringconvert.translate(None, '\'\]\[')
#        output.write("%s" % stringconvert)

output.close()
