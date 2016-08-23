#!/usr/bin/env python


# Purpose: To either unlink or link a service profile to a SP template
#	The idea is that we will unlink SPs from templates before upgrades so that changes to templates wont
#	cause a reboot. Hosts can then be relinked to the SP once they are ready to be upgraded.
#	
#	Highly recommend taking a UCSM backup before running this in case you lose the template mappings
#
# Outline
#	login
#	Loop through SPs figure out what SP they are associated to
#	Set the template in the description field
#	Link/Unlink the SP
# 	



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
parser.add_argument('-i', dest='hostname', action='store',
                    help='Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')
parser.add_argument('-l', dest='givemelist', action='store_true',
                    help='List all Profiles')
parser.add_argument('-a', dest='action', action='store',
                    help='Set to link or unlink')

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
template = {}
# Get Service Profiles
servers = handle.GetManagedObject(None, LsServer.ClassId()) 


for server in servers:
# Only want to check SPs that are instance type ie not Templates
	if server.Type == 'instance':
		if (args.givemelist):
			print server.Name
		        print server.Descr
			print server.SrcTemplName
# check to see if associated don't really care if its not
                elif "unlink" in args.action:
		   if server.OperSrcTemplName != '':
#			print server.Dn
                        setRsp = handle.SetManagedObject(server,LsServer.ClassId(), {LsServer.DN: server.Dn, LsServer.DESCR: server.SrcTemplName, LsServer.SRC_TEMPL_NAME: ""}) 
		   else:
                       setRsp = handle.SetManagedObject(server,LsServer.ClassId(), {LsServer.DN: server.Dn, LsServer.DESCR: "No Template" }) 
		elif "link" in args.action:
		   if server.Descr != 'No Template':
		       print server.Descr
                       setRsp = handle.SetManagedObject(server,LsServer.ClassId(), {LsServer.DN: server.Dn, LsServer.SRC_TEMPL_NAME: server.Descr }) 



handle.Logout
