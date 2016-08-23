#!/usr/local/Cellar/python/2.7.8_1/bin/python



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
import ssl
import time
import datetime
import sys
import getopt
import getpass
import argparse
import re
from UcsSdk import *
from collections import defaultdict

def loadAllMo():
    import os
    import UcsSdk
    exports = []
    globals_, locals_ = globals(), locals()
    package_path = os.path.dirname(UcsSdk.__file__)
    package_name = os.path.basename(package_path)
    mometa_path = os.path.join(package_path,'MoMeta')
    for filename in os.listdir(mometa_path):
        modulename, ext = os.path.splitext(filename)
        if not modulename.endswith('Meta') and ext in ('.py') and modulename != '__init__':
            subpackage = '{}.{}'.format(package_name+".MoMeta", modulename)
            module = __import__(subpackage, globals_, locals_, [modulename])
            modict = module.__dict__
            names = [name for name in modict if name[0] != '_']
            exports.extend(names)
            globals_.update((name, modict[name]) for name in names)

           

 

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
servers = handle.GetManagedObject(None, LsServer.ClassId())
for server in servers:
	print server.MaintPolicyName
	print server.Dn
	if not 'User-Ack' in server.MaintPolicyName:
		print "Need to add MaintPolicy"
#		getRsp=handle.GetManagedObject(None,LsServer.ClassId(),{OrgOrg.DN:server.Dn})
#		print getRsp
#		handle.SetManagedObject(getRsp,LsServer.ClassId(),{LsServer.MAINT_POLICY_NAME:"User-Ack"})
#		print "new policy name %s" % server.MaintPolicyName

print "----------------------------------------------------------------------------------------"
handle.Logout
sys.exit(0)


