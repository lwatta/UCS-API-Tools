#!/usr/local/Cellar/python/2.7.8_1/bin/python

# Purpose: To inventory the following from systems for FI-less configuration
# 	- map SP-name to Server
#	- get phys server serial number
#	- get phys server mgmt ip address

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
import ssl
#ssl._create_default_https_context=ssl._create_unverified_context

# get login arguments
parser = argparse.ArgumentParser(description='FI-less inventory script')
parser.add_argument('-i', dest='hostname', action='store',
                    help='Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

args = parser.parse_args()
#print(args.hostname)

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
#print "System ---"
#ucs_dimm_blacklist(handle)
#ucs_get_iom_firmware(handle)
#getNTPServers(handle)
#vlanCheck(handle)
# checking faults
#print "Checking Faults ---"
#ucs_get_faults(handle)

#print "Service Profiles ---"
# Get Service Profiles
servers = handle.GetManagedObject(None, IppoolAddr.ClassId()) 

for server in servers:
# Only want to check SPs that are instance type ie not Templates
   if server.Assigned == "yes":
	ipaddr = server.Id
        mcdn = server.AssignedToDn.replace("/ipv4-pooled-addr", "",1)
        getserial=handle.GetManagedObject(None,MgmtController.ClassId(),{MgmtController.DN: mcdn})[0]
        hw = mcdn.replace("/mgmt","",1)
        if "rack" in hw:
	  getrsp = handle.GetManagedObject(None,ComputeRackUnit.ClassId(),{ComputeRackUnit.DN: hw})[0]
        else:
	  getrsp = handle.GetManagedObject(None,ComputeBlade.ClassId(),{ComputeBlade.DN: hw})[0]
        print "%s | %s | %s | %s " % (getserial.Serial, ipaddr, hw, getrsp.AssignedToDn)
        
#	if server.Type == 'instance':
# check to see if associated don't really care if its not
#		if (server.AssocState == 'associated'):
#			print server.Name 
#			print server.PnDn
#		mcdn = server.PnDn + "/mgmt"
#			print mcdn
#		try:
#   		  getserial=handle.GetManagedObject(server,MgmtController.ClassId(),{MgmtController.DN: mcdn})[0]
#                except: 
#		  getserial="No Server details"
#			print getserial.Serial
#		mcipdn = getserial.Dn + "/ipv4-pooled-addr"
getip = handle.GetManagedObject(None,VnicIpV4PooledAddr.ClassId(),None)[0]
print getip
#		print "%s %s %s %s " % (server.Name, server.PnDn, getserial.Serial, getip.Addr)

				
handle.Logout


