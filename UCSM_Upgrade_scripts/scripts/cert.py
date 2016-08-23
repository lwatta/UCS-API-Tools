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
                                print "\t NIC %s \t Template %s" % (child.Name, child.OperNwTemplName)
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName

def ucs_get_vnic_profile_pending(handle, child):
	if child.AdaptorProfileName == 'TX_RX_OffloadOff':
		print "AdapterProfile is correctly set"
	else:
		print "AdapterProfile is not yet set to TX_RX_OffloadOff"
		print "This is not a problem yet"

def ucs_check_cert_status(handlelocal):
    getRsp = handlelocal.GetManagedObject(None,PkiKeyRing.ClassId())
    for i in getRsp:
      if "keyring-default" in i.Dn and "expired" in i.CertStatus:
          print bcolors.FAIL + "UCS SelfSigned Certificate has expired" + bcolors.ENDC
          print bcolors.FAIL + "Creating new Certificate. This will take a few minutes" + bcolors.ENDC
          print bcolors.FAIL + "This will also cause all connections to fail while key is regened" + bcolors.ENDC
          setRsp = handle.SetManagedObject(i,PkiKeyRing.ClassId(),{"Dn": "sys/pki-ext/keyring-default","Regen": "true"})
          
def ucs_get_faults(handlelocal):
    critical = 0
    major = 0
    minor  = 0
    warning = 0
    info = 0
    getRsp = handlelocal.GetManagedObject(None,FaultInst.ClassId())
    for fault in getRsp:
          if fault.Severity == "critical":
            critical = critical + 1
            if "VIF" in fault.Descr:
              print bcolors.FAIL + "Got VIF error on %s" % fault.Dn + bcolors.ENDC
              print bcolors.FAIL + "\tDescr is %s" % fault.Descr + bcolors.ENDC
          elif fault.Severity == "major":
            major = major + 1
            if "VIF" in fault.Descr:
              print bcolors.FAIL + "Got VIF error on %s" % fault.Dn + bcolors.ENDC
              print bcolors.FAIL + "\tDescr is %s" % fault.Descr + bcolors.ENDC
          elif fault.Severity == "minor":
            minor = minor +1
          elif fault.Severity == "warning":
            warning = warning + 1
          elif fault.Severity == "info":
            info = info + 1

    print bcolors.FAIL + "Critical is %s" % critical + bcolors.ENDC
    print bcolors.FAIL + "Major is %s" % major + bcolors.ENDC
    print bcolors.FAIL + "Minor is %s" % minor + bcolors.ENDC
    print bcolors.FAIL + "Warning is %s" % warning + bcolors.ENDC
    print bcolors.FAIL + "Info is %s" % info + bcolors.ENDC

def ucs_get_iom_firmware(handlelocal):
    print "Firmware Versions ->"
    getRsp=handlelocal.GetManagedObject('sys/switch-A',FirmwareStatus.ClassId(), {FirmwareStatus.DN:"sys/switch-A/fw-status"})[0]
    print "Switch-A Version -> %s" % getRsp.PackageVersion
    getRsp=handlelocal.GetManagedObject('sys/switch-B',FirmwareStatus.ClassId(), {FirmwareStatus.DN:"sys/switch-B/fw-status"})[0]
    print "Switch-B Version -> %s" % getRsp.PackageVersion
    getRsp=handlelocal.GetManagedObject(None,FirmwareRunning.ClassId())
    for i in getRsp:
        if 'slot' in i.Dn and 'fw-system' in i.Dn:
           print "%s Firmware version -> %s" % (i.Dn, i.Version)
        if i.Dn == 'sys/mgmt/fw-system':
           print "UCSM Firmware -> %s" % i.Version
     

def vlanCheck(handle):
# check to make sure vlans are not being used in the 3968 - 4047
    getRsp=handle.GetManagedObject(None,"FabricVlan",None)
    gotreserved = 0
    print "VLAN ->"
    for vlan in getRsp:
        if int(vlan.Id) > 3968:
           print bcolors.FAIL + "\tVLAN in reserved range -> %s" % vlan.Id + bcolors.ENDC
           gotreserved = 1
    if gotreserved == 0:
        print "\tVLANs are clean"    
		

def getNTPServers(handle):
    classId = "CommNtpProvider"
    crMos = handle.ConfigResolveClass(classId, None, inHierarchical=YesOrNo.FALSE, dumpXml=False)
    print "NTP ->"
    if crMos.OutConfigs.GetChild():
        for mo in crMos.OutConfigs.GetChild():
            if mo and mo.Name:
                print "\tNTP Name -> %s " % mo.Name
    else:
        print bcolors.FAIL + "\tNTP Not Set" + bcolors.ENDC

def ucs_sp_template(serverlocal,templatelocal):
   if 'initial' in templatelocal[serverlocal.OperSrcTemplName]:
	 print "\t Template -> %s" % serverlocal.OperSrcTemplName 
	 print bcolors.FAIL + "\t\t Updating -> NO!!!!" + bcolors.ENDC
   else:
	 print "\t Template -> %s" % serverlocal.OperSrcTemplName 
	 print "\t\t Updating -> Yes"

def ucs_sp_check(serverlocal):
#   print serverlocal.Dn
   if serverlocal.MaintPolicyName == '':
         print bcolors.FAIL + "\t Maintence Policy -> NO!!!" + bcolors.ENDC
   else:
       	 print "\t Maintence Policy -> %s" % serverlocal.MaintPolicyName

   if serverlocal.OperState in ('ok', 'unassociated'):
	 print "\t Server State -> %s" % serverlocal.OperState
   else:
	 print bcolors.FAIL + "\t Server State -> %s" % serverlocal.OperState + bcolors.ENDC
	
   if serverlocal.HostFwPolicyName =='':
	print bcolors.FAIL + "\t Firwmware Policy -> No!!!!" + bcolors.ENDC
   else:
	print "\t Firwmware Policy -> %s " % serverlocal.HostFwPolicyName 

   if serverlocal.BiosProfileName == '':
	print bcolors.FAIL + "\t Bios Policy -> NO!!!!" + bcolors.ENDC
   else:
	print "\t Bios Policy -> %s " % serverlocal.BiosProfileName
	

def ucs_check_for_faults(handle,serverlocal):
# basically any faults on passed handle. make it very generic. should be simple
   print serverlocal.Dn
   getRsp = handle.GetManagedObject(serverlocal.Dn, FaultInst.ClassId(), None, inHierarchical=True)
   for i in getRsp:
	print i

def ucs_dimm_blacklist(handlelocal):
# findout if dimm blacklisting is turned on
   getdimblack = handlelocal.GetManagedObject(None,ComputeMemoryConfigPolicy.ClassId(),None)[0]
   if "enabled" in getdimblack.BlackListing:
      print "\t DIMM BlackListing -> %s" % getdimblack.BlackListing
   else: 
      print bcolors.FAIL + "\t DIMM BlackListing  -> %s" % getdimblack.BlackListing + bcolors.ENDC
        	
def ucs_check_for_path(handlelocal,serverlocal):
# This will be tricky
#	using serverlocal.Dn get lsBinding classid
# 	from that output get PnDn
#	Getmanaged object (PnDn, AdapterUnit.ClassId())
   temp = serverlocal.Dn + "/pn"
   try:
      getHardware = handlelocal.GetManagedObject(serverlocal.Dn, LsBinding.ClassId(),{OrgOrg.DN:temp})[0]
   except: 
      print bcolors.FAIL + "\t Problem with LsBinding -> %s" % serverlocal.Dn + bcolors.ENDC
      return

   print "\t Physical host -> %s" % getHardware.PnDn
   if 'rack' in getHardware.PnDn:
       getAdapterInfo = handlelocal.GetManagedObject(getHardware.PnDn,ComputeRackUnit.ClassId(), None)[0]
   else:
       getAdapterInfo = handlelocal.GetManagedObject(getHardware.PnDn,ComputeBlade.ClassId(), None)[0]
   print "\t Configured Paths -> %s" % getAdapterInfo.ConnStatus
   print "\t Path Status -> %s" % getAdapterInfo.ConnPath

# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)

ucs_check_cert_status(handle)
handle.Logout

