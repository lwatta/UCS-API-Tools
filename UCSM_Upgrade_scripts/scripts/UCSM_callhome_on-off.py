#!/usr/bin/env python


# Purpose: Will turn call home off or on depending on the options given
#	To be used for CRs where we don't want UCSM to send call home messages

# Outline
#	login
#	check the args to either turn it on or turn it off
#	Do the action



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
parser = argparse.ArgumentParser(description='Turns callhome on or off. You need to supply the UCS system, password and action. If no action then it just shows the current status')
parser.add_argument('-u', dest='ucshostname', action='store',
                    help='UCS Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')
parser.add_argument('-a', dest='upordown', action='store',
                    help='Optional {on/off}')


args = parser.parse_args()

# Login first
handle = UcsHandle()
handle.Login(args.ucshostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, CallhomeEp.ClassId(),None)
# Real simple check to make sure CallHome is enabled
#print getRsp[0]
rsp = getRsp[0]
if rsp.AdminState != "on":
	print "Hostname --> %s" % args.ucshostname 
	print "*--------------- AdminState > %s  --------------------*" % rsp.AdminState
else:
	print "Hostname --> %s" % args.ucshostname 
	print "*--------------- AdminState > %s  --------------------*" % rsp.AdminState
if not args.upordown:
	print "No action specified. Just showing status"
	handle.Logout
	sys.exit(0)

if args.upordown == "on":
	print "turning callhome back on"
	handle.SetManagedObject(getRsp,CallhomeEp.ClassId(),{"AdminState":"on"})
else:
	print "turning callhome back off"        
	handle.SetManagedObject(getRsp,CallhomeEp.ClassId(),{"AdminState":"off"})

getRsp = handle.GetManagedObject(None, CallhomeEp.ClassId(),None)[0]
print getRsp
handle.Logout
sys.exit(0)


