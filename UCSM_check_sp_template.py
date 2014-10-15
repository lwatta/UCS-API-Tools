#!/usr/bin/python


# Purpose: To check and see if every nova and net node is associated/bound to an SP template
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
from UcsSdk import *
from collections import defaultdict

# get login arguments
parser = argparse.ArgumentParser(description='Script to make sure Nova and Net SPs are associated to an updating template')
parser.add_argument('-u', dest='hostname', action='store',
                    help='Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')
parser.add_argument('-l', dest='givemelist', action='store_true',
                    help='List all Profiles')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

args = parser.parse_args()
#print(args.hostname)
def ucs_get_vnictemplate(handle, server):
        childs = handle.ConfigResolveChildren(VnicEther.ClassId(), server.Dn, None, YesOrNo.TRUE)
        for child in childs.OutConfigs.GetChild():
# we are looking for Vnic2 if Nova and Vnic2 and Vnic3 if Net
                if ('vnic2' in child.Name.lower() and ('nova' in server.Name.lower() or 'net' in server.Name.lower())):
                        if not child.OperNwTemplName:
                                print bcolors.FAIL + "\t NIC %s \tNo Template " % child.Name + bcolors.ENDC
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName
                        else:
                                print "\t NIC %s \tTemplate %s" % (child.Name, child.OperNwTemplName)
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName
                elif ( ('vnic2' in child.Name.lower() or 'vnic3' in child.Name.lower()) and 'net' in server.Name.lower() ):
                        if not child.OperNwTemplName:
                                print bcolors.FAIL + "\t NIC %s \tNo Template" % child.Name + bcolors.ENDC
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName
                        else:
                                print "\t NIC %s \tTemplate %s" % (child.Name, child.OperNwTemplName)
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName

def ucs_get_vnic_profile_pending(handle, child):
	if child.AdaptorProfileName == 'TX_RX_OffloadOff':
		print "AdapterProfile is correctly set"
	else:
		print "AdapterProfile is not yet set to TX_RX_OffloadOff"
		print "This is not a problem yet"


# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
#print "getRsp ---- "
#print getRsp
#print "getRsp ---- "
template = {}
# Get Service Profiles
servers = handle.GetManagedObject(getRsp, LsServer.ClassId()) 

# Check to make sure templates are updating
for servertemplate in servers:
# check for templates
	if servertemplate.Type != 'instance':
		template[servertemplate.Dn] = servertemplate.Type

print "end templates"

for server in servers:
# Only want to check SPs that are instance type ie not Templates
	if server.Type == 'instance':
		if (args.givemelist):
			print server.Name
# check to see if associated don't really care if its not
		elif (server.AssocState == 'associated' and server.OperSrcTemplName != ''):
#		print "got a real instance. Now check to see if nova or net"
#			print server.Dn
			if "nova" in server.Dn.lower():
				if 'initial' in template[server.OperSrcTemplName]:
					 print "SP -> %s" % server.Name
					 print "\t Template -> %s" % server.OperSrcTemplName 
					 print bcolors.FAIL + "\t\t Updating -> NO!!!!" + bcolors.ENDC
				else:
					if server.MaintPolicyName == '':
						print "SP -> %s" % server.Name
						print "\t Template -> %s" % server.OperSrcTemplName 
						print "\t\t Updating -> Yes"
						print bcolors.FAIL + "\t\t\tMaintence Policy -> NO!!!" + bcolors.ENDC
					else:
						print "SP -> %s" % server.Name
						print "\t Template -> %s" % server.OperSrcTemplName 
						print "\t\t Updating -> Yes"
						print "\t\t\tMaintence Policy -> %s" % server.MaintPolicyName

				ucs_get_vnictemplate(handle,server)

			elif "net" in server.Dn.lower():
				if 'initial' in template[server.OperSrcTemplName]:
					print "SP -> %s " % server.Name
					print "\tTemplate -> %s"  % server.OperSrcTemplName
					print bcolors.FAIL + "\t\tUpdating -> NO!!!!" + bcolors.ENDC
				else:
					if server.MaintPolicyName == '':
						print "SP -> %s " % server.Name
						print "\tTemplate -> %s"  % server.OperSrcTemplName
						print "\t\tUpdating -> Yes"
						print bcolors.FAIL + "\t\t\tMaintence Policy -> NO!!!" + bcolors.ENDC
					else:
						print "SP -> %s " % server.Name
						print "\tTemplate -> %s"  % server.OperSrcTemplName
						print "\t\tUpdating -> Yes"
						print "\t\t\tMaintence Policy -> %s" % server.MaintPolicyName
		                ucs_get_vnictemplate(handle,server)



		elif (server.AssocState == 'associated' and server.OperSrcTemplName == ''):
			if ('nova' in server.Dn.lower() or 'net' in server.Dn.lower() ):
                                print "SP -> %s" % server.Name 
				print bcolors.FAIL + "\tTemplate -> Not Assigned WARNING!!!! " + bcolors.ENDC
		                ucs_get_vnictemplate(handle,server)
				


handle.Logout
