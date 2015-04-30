#!/usr/bin/python


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
#
# Outline
#	login
#	Loop through all SPs and check for pending reboot status



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
parser = argparse.ArgumentParser(description='Checks to see if SP has pending reboot and if so shove to stdout. ')
parser.add_argument('-u', dest='ucshostname', action='store',
                    help='UCS Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')


args = parser.parse_args()
#temp = re.search("(nova.*)", source)
#nova_name = temp.group()

# Login first
handle = UcsHandle()
handle.Login(args.ucshostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
template = {}
# Get Service Profiles
servers = handle.GetManagedObject(getRsp, LsServer.ClassId()) 
# Check to make sure templates are updating
for serviceprofile in servers:
# check for name
	if (serviceprofile.Type == 'instance' and 'nova' in serviceprofile.Name):
		print "Service profile %s" % serviceprofile.Name
		print "Check opstate %s " % serviceprofile.OperState
#		if serviceprofile.OperState == "pending-reboot":
#			print "Service profile %s" % serviceprofile.Name
#			print "Check opstate %s " % serviceprofile.OperState

handle.Logout

