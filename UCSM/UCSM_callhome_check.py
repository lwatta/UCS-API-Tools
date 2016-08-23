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
parser = argparse.ArgumentParser(description='Checks to see if callhome is enabled on the UCS system. Eventrually will configure it \
		if it is not configured. ')
parser.add_argument('-u', dest='ucshostname', action='store',
                    help='UCS Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')


args = parser.parse_args()

# Login first
handle = UcsHandle()
handle.Login(args.ucshostname, "admin", args.password)
#getRsp = handle.GetManagedObject(None, CallhomeEp.ClassId(),None)[0]
childs = handle.GetManagedObject(None, CallhomeProfile.ClassId(), {"Dn": "call-home/profile-short_txt"})[0]
print childs
print "Warning Level -----> %s" % childs.Level
putRsp = handle.SetManagedObject(childs.Dn, CallhomeProfile.ClassId(), {"Level":"minor", "Dn": childs.Dn}, True)
childs = handle.GetManagedObject(None, CallhomeProfile.ClassId(), None)[0]
print "Warning Level -----> %s" % childs.Level
# Real simple check to make sure CallHome is enabled
#if getRsp.AdminState != "on":
#	print "Hostname --> %s" % args.ucshostname 
#	print "AdminState > %s" % getRsp.AdminState
#else:
#	print "Hostname --> %s" % args.ucshostname 
#	print "AdminState > %s" % getRsp.AdminState

# Check the contact details
#contact = handle.GetManagedObject(None, CallhomeSource.ClassId(), None)
#for key in contact:
#	print key
# Now check the profiles
#childs = handle.GetManagedObject(None, CallhomeProfile.ClassId(), None)
#for child in childs:
#	if "CiscoTAC" in child.Name:
#		print "\tName ------> %s" % child.Name
#		print "\tDescr -----> %s\n" % child.Descr
#		emails = handle.GetManagedObject(child.Dn, CallhomeDest.ClassId(), None, inHierarchical=True)
#		for email in emails:
#			if child.Name in email.Dn:
#				print email.Email
#
#policies = handle.GetManagedObject(None, CallhomePolicy.ClassId(), None)
#for policy in policies:
#	print policy

#smtp = handle.GetManagedObject(None, CallhomeSmtp.ClassId(), None)
#for key in smtp:
#	print "\t\tMail Server------> %s" % key.Host

# Send test email
#print "send testalert"
#handle.AddManagedObject(getRsp.Dn, CallhomePeriodicSystemInventory.ClassId(), {"SendNow":"yes", "Dn":"call-home/CallhomePeriodicSystemInventory"}, True)
#print "end send testalert"
print "----------------------------------------------------------------------------------------"
handle.Logout
sys.exit(0)


