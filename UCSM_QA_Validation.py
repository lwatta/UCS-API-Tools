#!/usr/bin/python

# Purpose: Verify that a UCS installation is correctly configured before go live
# 	Check for various issues so that we know everything is correctly configured
#	Eventually UCS director might be able to do this

# Outline
#	Login
#	Check the following for correctness
#		UUID Pool
#		MAC Pool
#	  	Global Policies for
#			ChassisDiscovery Policy
#			Rack Server Discovery
#			Power Policy	
#		Firmware policy
#		Local disk Policy
#		Maintenance Policy
#		
#		Nic templates
#			Make sure they exist
#			correct primary fabric
#			are updating templates

#	--- That's for now ----
#		Add Service Template checks
#			Does the right SP templates exist
#				Do they have the correct settings



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
		if ('vnic2' in child.Name.lower() and ('nova' in server.Name.lower() or 'net' in server.Name.lower()) ):
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

#def ucs_check_SP_template(handle,child):
# Things to check
#	Policies are set (maintenance, boot, firmware, bios)
#	Pools are set (UUID,Mac,server)
#	Updating template
#	vNIC templates are correct

def ucs_get_vnic_profile_pending(handle, child):
	if child.AdaptorProfileName == 'TX_RX_OffloadOff':
		print "AdapterProfile is correctly set"
	else:
		print "AdapterProfile is not yet set to TX_RX_OffloadOff"
		print "This is not a problem yet"

def ucs_check_global(handle):
	print "Checking Chassis Discovery Policy "
	tempRsp=handle.GetManagedObject(None,ComputeChassisDiscPolicy.ClassId(),None)[0]
	if tempRsp.Action == "platform-max":
		print "\tChassis Discovery Policy is %s" % tempRsp.Action
	else:
		print bcolors.FAIL + "\tChassis Discovery Policy is not platform-max" + bcolors.ENDC 
	if tempRsp.LinkAggregationPref == "port-channel":
		print "\tChassis Link Aggregation is %s" % tempRsp.LinkAggregationPref
	else:
		print bcolors.FAIL + "\tChassis Link Aggregation is not port-channel" + bcolors.ENDC
	print "Checking Rack Server Discovery"
	tempRsp=handle.GetManagedObject(None,ComputeServerDiscPolicy.ClassId(),None)[0]
	if tempRsp.Action == "immediate":
		print "\tRack Server Discovery Policy is %s" % tempRsp.Action
	else:
		print bcolors.FAIL + "\tRack Server Discovery Policy is not immediate" + bcolors.ENDC 
	print "Checking PSU Redundancy"
	tempRsp=handle.GetManagedObject(None,ComputePsuPolicy.ClassId(),None)[0]
	if tempRsp.Redundancy == "grid" or tempRsp.Redundancy == "n+1":
		print "\tPSU Redundancy is %s" % tempRsp.Redundancy
	else:
		print bcolors.FAIL + "\tPSU Redundancy is not GRID or N+!" + bcolors.ENDC 
		print tempRsp.Redundancy

def ucs_check_vnic_templates(handle,nic,primaryfabric):
	print "Checking vNIC Template %s" % nic
	vnic=handle.GetManagedObject(None,VnicLanConnTempl.ClassId(),{OrgOrg.DN:nic})[0]
	if vnic:
		print "\t\tVNIC Template %s exists" % nic
	else:
		print bcolors.FAIL + "\t\tVNIC Template %s does not exist" + bcolors.ENDC % nic
# Next check for fabric failover
# 	failover is captured with SwitchID and would show both switches A-B or B-A
	if primaryfabric == "A":
		if vnic.SwitchId == "A-B":
			print "\t\tVNIC Template Primary is A"
			print "\t\tVNIC Template Failover is correct"
		elif vnic.SwitchId == "A":
			print "\t\tVNIC Template Primary is A"
			print bcolors.FAIL + "\t\tVNIC Template Failover is not set" + bcolors.ENDC 
		elif vnic.SwitchId == "B-A":
			print bcolors.FAIL + "\t\tVNIC Template Primary is B" + bcolors.ENDC 
			print "\t\tVNIC Template Failover is set"
		else:
			print bcolors.FAIL + "\t\tVNIC Template Primary is B" + bcolors.ENDC 
			print bcolors.FAIL + "\t\tVNIC Template Failover is not set" + bcolors.ENDC 
	elif primaryfabric == "B":
		if vnic.SwitchId == "B-A":
			print "\t\tVNIC Template Primary is B"
			print "\t\tVNIC Template Failover is correct"
		elif vnic.SwitchId == "B":
			print "\t\tVNIC Template Primary is B"
			print bcolors.FAIL + "\t\tVNIC Template Failover is not set" + bcolors.ENDC 
		elif vnic.SwitchId == "A-B":
			print bcolors.FAIL + "\t\tVNIC Template Primary is A" + bcolors.ENDC 
			print "\t\tVNIC Template Failover is set"
		else:
			print bcolors.FAIL + "\t\tVNIC Template Primary is A" + bcolors.ENDC 
			print bcolors.FAIL + "\t\tVNIC Template Failover is not set" + bcolors.ENDC 

# Check to see if the template is updating
	if vnic.TemplType == "updating-template":
		print "\t\tVNIC Template is Updating"
	else:
		print bcolors.FAIL + "\t\tVNIC Template is not Updating" + bcolors.ENDC

# Check MACpool
	if vnic.IdentPoolName == "CiscoIT-MAC":
		print "\t\tVNIC Template has correct MAC Pool %s" % vnic.IdentPoolName
	else:
		print bcolors.FAIL + "\t\tVNIC Template has wrong MAC Pool %s" + bcolors.ENDC % vnic.IdentPoolName

def ucs_check_policies(handle):
	print "Checking SP Policies"
	print "\tChecking Firmware Policy"
	fwpolicy=handle.GetManagedObject(None,FirmwareComputeHostPack.ClassId(),{OrgOrg.DN:"org-root/fw-host-pack-Host-FW-2.2.1b"})[0]		
	if fwpolicy:
		print "\t\tFirmware Policy %s exists" % fwpolicy.Name
    	else:
		print bcolors.FAIL + "\t\tFirmware Policy 2.2(1b)B does not exist" + bcolors.ENDC

    	print "\tChecking Local Disk Policy"
	ldpolicy=handle.GetManagedObject(None,StorageLocalDiskConfigPolicy.ClassId(),{OrgOrg.DN: "org-root/local-disk-config-Mirrored-Disk"})[0]
        if ldpolicy:
		print "\t\tLocalDisk Policy %s exists" % ldpolicy.Name
	else:
		print bcolors.FAIL + "\t\tLocalDisk Policy raid-mirrored does not exist" + bcolors.END

	ldpolicy=handle.GetManagedObject(None,StorageLocalDiskConfigPolicy.ClassId(),{OrgOrg.DN: "org-root/local-disk-config-default"})[0]
        if ldpolicy:
		print "\t\tLocalDisk Policy %s exists" % ldpolicy.Name
	else:
		print bcolors.FAIL + "\t\tLocalDisk Policy any-configuration does not exist" + bcolors.END
	

	print "\tChecking Maintenance Policy"
	fwpolicy=handle.GetManagedObject(None,LsmaintMaintPolicy.ClassId(),{OrgOrg.DN: "org-root/maint-User_Ack"})[0]
	if fwpolicy:
		print "\t\tMaintence Policy %s exists" % fwpolicy.Name
	else:
		print bcolors.FAIL + "\t\tMaintenance Policy User_Ack does not exist" + bcolors.END
		
	print "end"

		

def ucs_check_SPtemplateNova(handle,child):
	print "\tChecking Template %s" % child.Name

def ucs_check_pools(handle):
	print "Checking for Pools"
	print "\tChecking for UUID Pool"
	uuidpool=handle.GetManagedObject(None,UuidpoolPool.ClassId(),None)
	found=0
	for pool in uuidpool:
		if pool.Name == "CiscoIT-UUID":
			print "\t\tUUID Pool %s exists" % pool.Name
			if pool.Size == "255":
				print "\t\t\tUUID Pool Size is %s" % pool.Size
			else:
				print bcolors.FAIL + "\t\t\tUUID Pool Size is not 255" + bcolors.ENDC
			found =1
			break	
	if not found:
		print bcolors.FAIL + "\t\tUUID Pool CiscoIT-UUID does not exist" + bcolors.ENDC	

	macpool=handle.GetManagedObject(None,MacpoolPool.ClassId(),None)
	found=0
	for pool in macpool:
                if pool.Name == "CiscoIT-MAC":
                        print "\t\tMAC Pool %s exists" % pool.Name
                        if pool.Size == "255":
                                print "\t\t\tMAC Pool Size is %s" % pool.Size
                        else:
                                print bcolors.FAIL + "\t\t\tMAC Pool Size is not 255" + bcolors.ENDC
                        found =1
                        break
        if not found:
                print bcolors.FAIL + "\t\tUUID Pool CiscoIT-MAC does not exist" + bcolors.ENDC
	
	
	
# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
#print "getRsp ---- "
#print getRsp
#print "getRsp ---- "
ucs_check_global(handle)
ucs_check_pools(handle)
ucs_check_policies(handle)

# Check vnic templates.
#	Cycle through the list of templates that should be created and make sure they are correct.
#	calls should be something like ucs_check_vnic_template(handle,vnic,primaryfabric)
# list of templates
print "Checking VNIC Templates"
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-Nova-vNic3-eth2","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-Nova-vNic2-eth1","B")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-Nova-vNic1-eth0","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-Srvc-vNic1-eth0","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-MGMT-vNIC1-eth0","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-Net-vNic3-eth2","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-DMZ-vNIC1-eth0","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-Bld_Ceph_Priv","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-Bld_Ceph_Pub","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-DMZ-vNIC1-eth0","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-VirtInfra-eth1","A")
ucs_check_vnic_templates(handle,"org-root/lan-conn-templ-VirtInfra-eth0","A")

# SP dictionary
SPdict = {"dn":'org-root/ls-Nova-Server-ephemeral', "maintpolicy":'maint-User_Ack', "firmwarepolicy":'Host-FW-2.21b', "biospolicy":'SRIOV', "localdiskpolicy":'Static-Disk', "bootorder":'eth0', "uuidpool":'CiscoIT-UUID', "vnic0":'org-root/lan-conn-templ-Nova-vNic1-eth0 ', "vnic1":'org-root/lan-conn-templ-Nova-vNic2-eth1 ', "vnic2":'org-root/lan-conn-templ-Nova-vNic3-eth2', "vnic0apolicy":'Linux', "vnic1apolicy":'TXRX_OffloadOff', "vnic2apolicy":'Linux'}
handle.Logout


sys.exit(0)

#template = {}

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
# if its not an instance its a template so check templates here
	elif server.Type == "updating-template":
		print "Call check templates code"
				

