#!/usr/bin/env python


# Purpose: Will queury UCSM for SPs and then see if they have pending changes
#	It looks like ther are several places where the pending changes can be queried under lsServer
# 	For one there is an lsmaintAck MO. If you query that object some useful variables seem to be
#		operstate = waiting-for-user
#		changes = networking,operational-policies
#
#	lsServerFSM
#		fsmStatus will show as inProgress
#		currentFSM will show as Configure
#	vnicEther
#		Should show the new adapterProfileName
#	
#	This will flesh out any SPs that have been unbound for some reason and won't get the adapter-profile update
#
# Outline
#	login
#	Loop through SPs that have nova or net in the name
#	Check each one for assication to a template
#	Raise alarm for any SP that is not associated.



# Import crap
import simplejson as json
import time
import datetime
import sys
import getopt
import getpass
import argparse
import re
from UcsSdk import *
from collections import defaultdict

# get login arguments
parser = argparse.ArgumentParser(description='Get faults for specific host. Guess based off the hostname. \
		Not perfect because hostnames and SPs do not always match. ')
parser.add_argument('-i', dest='ucshostname', action='store',
                    help='UCS Hostname')
parser.add_argument('-u', dest='ucsusername', action='store',
                    help='UCS Username')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')
parser.add_argument('-n', dest='hostname', action='store',
                    help='hostname to reset')
parser.add_argument('-e', dest='exact', action='store_true',
                    help='Do not try to match the hostname take exactly what is passed in')


args = parser.parse_args()
source = args.hostname
if not args.exact:
	temp = re.search("(nova.*)", source)
	nova_name = temp.group()
else:
	nova_name = source
# Login first
handle = UcsHandle()
handle.Login(args.ucshostname, args.ucsusername, args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
template = {}
# Get Service Profiles
servers = handle.GetManagedObject(getRsp, LsServer.ClassId()) 
exact = 0
duplicates = 0
# Check to make sure templates are updating
for serviceprofile in servers:
# check for name
	if (serviceprofile.Type == 'instance' and nova_name in serviceprofile.Name):
		print "found it"
		print "now do exact check"
		if serviceprofile.Name == source:
			print "exact match"
			print serviceprofile.Name
			dnuse = serviceprofile
			print nova_name
			exact = 1
			break
		else:
			if duplicates == 1:
				print "crap got duplicates"
			duplicates = duplicates +1	
			newsource = serviceprofile.Name	
			dnuse = serviceprofile

if exact == 1:
	print "we got exact so use that. Use source"
        print "Operational State: %s" % dnuse.OperState
        faults = handle.GetManagedObject(dnuse,FaultInst.ClassId(), {OrgOrg.DN: dnuse.Dn})
        for i in faults:
		print i
elif duplicates ==1:
	print "we got a single match so use that"
        print "Operational State: %s" % dnuse.OperState
        faults = handle.GetManagedObject(dnuse,FaultInst.ClassId(), {OrgOrg.DN: dnuse.Dn})
        for i in faults:
		print i
elif duplicates > 1:
	print "we got duplicates so we are fucked"
	handle.Logout
	sys.exit(1)
else:
	print "we got nothing so stop"
	handle.Logout
	sys.exit(1)

handle.Logout
