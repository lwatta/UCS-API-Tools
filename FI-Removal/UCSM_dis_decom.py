#!/usr/local/Cellar/python/2.7.8_1/bin/python



# Purpose: To check things before an upgrade.
#	Things to check for
#	- no vlans higher than 3900 - check
#	- check for ntp enabled - check
#	- Any faults. Major faults 
#       - server-profile checks
#       	- Check all blades for being assigned to template
#  	     	- Check that blades have firmware policy
#      	 	- Check that blades have bios policy changes (check before and after)
#		- Verify set to user-ack for mgmt policy
#		- check that A and B path are valid
#	- get firmware versions
#		Check FI firmware
#		Check IOM firmware
#   		Check UCSM firmware
#       - Check for dimm blacklisting
#	- Print total number of errors for all types
#       - Check for an VIF errors. VIF errors need to be fixed before you can proceed
#
# Outline
#	login
#	Loop through all SPs 
#	Check each one for assication to a template
#	Raise alarm for any SP that is not associated.
#
# 10/12/2105 lwatta
# 	Added check for cert expiration and if cert is invalide to create a new one.


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
                                print "\t NIC %s \t Template %s" % (child.Name, child.OperNwTemplName)
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName

def ucs_disassociate(handlelocal,serverlocal):
   temp = serverlocal.Dn + "/pn"
   try:
      getHardware = handlelocal.GetManagedObject(serverlocal.Dn, LsBinding.ClassId(),{OrgOrg.DN:temp})
   except: 
      print bcolors.FAIL + "\t Problem with LsBinding -> %s" % serverlocal.Dn + bcolors.ENDC
      return

   print "\t Physical host -> %s" % getHardware[0].PnDn
   print "Disassociate ----->"
   rsp1=handle.RemoveManagedObject(getHardware)

def ucs_decom(handlelocal):
# Decom all servers starting with blades first ComputeBlade then ComputeRackUnit
   print "decom all blades"
   getrsp = handlelocal.GetManagedObject(None,ComputeBlade.ClassId())
   for i in getrsp:
      print "decom %s" % i.Rn
      dcomcompute=handlelocal.SetManagedObject(i,ComputeBlade.ClassId(),{ComputeBlade.DN: i.Dn, ComputeBlade.LC: "decommission"})
   print "Sleep for 120 "
   time.sleep(60)
   
   print "decom all rackunits"
   getrsp = handlelocal.GetManagedObject(None,ComputeRackUnit.ClassId())
   for i in getrsp:
      print "decom %s" % i.Rn
      dcomrack=handlelocal.SetManagedObject(i,ComputeRackUnit.ClassId(),{ComputeBlade.DN: i.Dn, ComputeBlade.LC: "decommission"})

# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
#print "getRsp ---- "
#print getRsp
#print "getRsp ---- "
template = {}

# check for NTP
print "System ---"
#ucs_dimm_blacklist(handle)
#ucs_get_iom_firmware(handle)
#getNTPServers(handle)
#vlanCheck(handle)
# checking faults
print "Checking Faults ---"
#ucs_get_faults(handle)

print "Service Profiles ---"
# Get Service Profiles
servers = handle.GetManagedObject(getRsp, LsServer.ClassId()) 

# Check to make sure templates are updating
for servertemplate in servers:
# check for templates
	if servertemplate.Type != 'instance':
		template[servertemplate.Dn] = servertemplate.Type


for server in servers:
# Only want to check SPs that are instance type ie not Templates
	if server.Type == 'instance':
		if (args.givemelist):
			print server.Name

# check to see if associated don't really care if its not
		elif (server.AssocState == 'associated' and server.OperSrcTemplName != ''):
#			print server.Dn
                        print "SP -> %s" % server.Name
#			ucs_sp_template(server,template)
#			ucs_sp_check(server)
			ucs_disassociate(handle,server)




		elif (server.AssocState == 'associated' and server.OperSrcTemplName == ''):
			print "SP -> %s" % server.Name 
			print bcolors.FAIL + "\t Template -> Not Assigned WARNING!!!! " + bcolors.ENDC
#		        ucs_sp_check(server)
#			ucs_check_for_faults(handle,server)
			ucs_disassociate(handle,server)
				

ucs_decom(handle)

handle.Logout


