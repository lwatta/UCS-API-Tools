#!/usr/bin/env python


# Purpose: Will set the FW policy on every template
#
# Outline
#	login
#	Loop through SPs and find templates
#       Set FW policy for the templates to the passed in argument
#


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
parser = argparse.ArgumentParser(description='Checks to see if SP has pending reboot and if so it reboots it. Also trys to match \
		the nova name with the sp name by searching for nova#-XXX in name of the template. ')
parser.add_argument('-i', dest='ucshostname', action='store',
                    help='UCS Hostname')
parser.add_argument('-u', dest='username', action='store',
                    help='Admin username', default='admin')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')
parser.add_argument('-f', dest='fwpolicy', action='store',
                    help='FW policy to set on templates')


args = parser.parse_args()
if not args.fwpolicy:
        print "Error need to set FW policy at command line like Host-FW-2.2.5a"
	sys.exit(1)

# Login first
handle = UcsHandle()
handle.Login(args.ucshostname, "admin", args.password)

# Get Service Profiles
servers = handle.GetManagedObject(None, LsServer.ClassId()) 

# Check to make sure templates are updating
for serviceprofile in servers:
# check for name
        print serviceprofile
	if "template" in serviceprofile.Type:
#		print "found it %s" % serviceprofile.Name
#		print "FirmwarePolicy is "
#		print serviceprofile.HostFwPolicyName
		getRsp = handle.SetManagedObject(serviceprofile,LsServer.ClassId(), {LsServer.DN: serviceprofile.Dn, LsServer.HOST_FW_POLICY_NAME: args.fwpolicy})

handle.Logout
