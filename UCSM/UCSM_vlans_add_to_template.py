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
parser.add_argument('-t', dest='template', action='store',
                    help='Vnic Template like  org-root/lan-conn-templ-Nova-vNic2-eth1')
parser.add_argument('-f', dest='vlanfile', action='store',
                    help='File of vlans to add to the template.Simple list of vlan numbers\
			This option implies you are adding vlans. Leave it off to not add')
parser.add_argument('-l', dest='list', action='store',
                    help='List vlans for template only. Requires -t')


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
				get_vnic_vlans(handle,child,child.OperNwTemplName)
                elif ( ('vnic2' in child.Name.lower() or 'vnic3' in child.Name.lower()) and 'net' in server.Name.lower() ):
                        if not child.OperNwTemplName:
                                print bcolors.FAIL + "\t NIC %s \tNo Template" % child.Name + bcolors.ENDC
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName
                        else:
                                print "\t NIC %s \tTemplate %s" % (child.Name, child.OperNwTemplName)
				print "\t\tAdapterProfile %s" % child.AdaptorProfileName
				get_vnic_vlans(handle,getRsp,child.OperNwTemplName)

def ucs_get_vnic_profile_pending(handle, child):
	if child.AdaptorProfileName == 'TX_RX_OffloadOff':
		print "AdapterProfile is correctly set"
	else:
		print "AdapterProfile is not yet set to TX_RX_OffloadOff"
		print "This is not a problem yet"

def get_vnic_vlans(handle,child,template):
#    dnme = 'org-root/' + template
    i = 0
    print template
    vnictempl = handle.GetManagedObject(child, VnicLanConnTempl.ClassId(), {OrgOrg.DN: template})[0]
    print vnictempl 
    vlans = handle.ConfigResolveChildren(VnicEtherIf.ClassId(), vnictempl.Dn, None, YesOrNo.TRUE)
    for t in vlans.OutConfigs.GetChild():
        print t.Dn
        i = i + 1
    print "Total Vlans ===> %s" % i

def add_vlans(handle,child,template,vlan):
# lets add a vlan to the template
    print "Add vlan.Dn %s To template %s " % (vlan.Dn, template)
#    adddn = template + "/if-" + vlan.Name
#    vnictempl = handle.GetManagedObject(child, VnicLanConnTempl.ClassId(), {OrgOrg.DN: template})[0]
#    try: 
#        addvlan = handle.AddManagedObject(vnictempl, VnicEtherIf.ClassId(), {"DefaultNet": "no", "Name": vlan.Name, "Dn": adddn}) 
#    except Exception, err:
#	print bcolors.FAIL + "Exception:", str(err) + bcolors.ENDC
#        import traceback, sys
#        print bcolors.FAIL + '-'*60 + bcolors.ENDC
#        traceback.print_exc(file=sys.stdout)
#        print bcolors.FAIL + '-'*60  + bcolors.ENDC



# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)
if args.list:
	print "we are listing the vlans for %s" % args.template
   	splist = handle.GetManagedObject(None,LsServer.ClassId())
	for i in splist:
		print i.Name
		ucs_get_vnictemplate(handle,i) 
elif args.vlanfile:
	print "We are adding vlans from file %s" % args.vlanfile
        for templine in open(args.vlanfile).readlines():
	   vlan = templine.rstrip('\r\n')
	   ucsvlan = handle.GetManagedObject(None, FabricVlan.ClassId(), {"Id": vlan})
	   if not ucsvlan:
		print bcolors.FAIL + "Vlan %s Does not exist. Please create the VLAN on the UCS system" % vlan + bcolors.ENDC
           else: 
 		add_vlans(handle,"None",args.template,ucsvlan[0])
else:
	getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
	template = {}
# Get Service Profiles
	get_vnic_vlans(handle,getRsp,args.template)

handle.Logout
