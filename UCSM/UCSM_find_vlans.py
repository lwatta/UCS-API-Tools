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
parser = argparse.ArgumentParser(description='Run single ucs api command to test something ')
parser.add_argument('-u', dest='ucshostname', action='store',
                    help='UCS Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')


args = parser.parse_args()

# Login first
handle = UcsHandle()
handle.Login(args.ucshostname, "admin", args.password)
# check to make sure vlans are not being used in the 3968 - 4047
getRsp=handle.GetManagedObject(None,"FabricVlan",None)
gotreserved = 0
print "VLAN ->"
for vlan in getRsp:
  if int(vlan.Id) > 599 and int(vlan.Id) < 700:
    print "\tVLAN -> %s" % vlan.Id 


print "----------------------------------------------------------------------------------------"
handle.Logout
sys.exit(0)


