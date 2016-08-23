#!/usr/bin/env python

# Purpose: Take simple UCS information in yaml configuration and iterate through it making changes
# yaml config should take a classid and then settings that should be changed.
# including DN in the yaml file
# won't work for all UCS configs as some things require additional processing. This is mean for simple changes
# 	much like the CIMC settings for standalone.

# Usage: ./check_or_modify_VIC_tcploffload.py -a $slot_num -c $interface_yaml-file -o $ovs_vnics_params.yml -l $linux_vnics_params.yml -m $request_to_modify -i cimc_ip -u admin -p $password
# Example of survey: ./check_or_modify_VIC_tcploffload.py -a 1 -c vnics_service_cloud.yml -o ovs_vnics_params.yml -l linux_vnics_params.yml -i mel2-csm-a-nova2-001-r -u admin -p xxx
# Example of modify: ./check_or_modify_VIC_tcploffload.py -a 1 -c vnics_service_cloud.yml -o ovs_vnics_params.yml -l linux_vnics_params.yml -m True -i mel2-csm-a-nova2-001-r -u admin -p xxx

from UcsSdk import *
import argparse
import yaml

def checkAndModifyProfile (ucs, classid, desired_settings,  modify_requested_flag):
    profile_res = ucs.GetManagedObject(None, classid, None, inHierarchical=True)
    
    for children in profile_res:
        curr_class = profile_res[0].__dict__
        for subclass, subvalues in desired_settings.iteritems():
            print subclass
            print curr_class["classId"]
            for subvaluekey, subvalueitem in subvalues.iteritems():
		print subvaluekey
		print subvalueitem
		curr_value = getattr(children,subvaluekey)
		print "%s current value: [%s] desired value: [%s]" %(biosoption, curr_value, value)
                profile_updates[biosoption] = value
            if (modify_requested_flag == 'True'):
                print "-------------- make change ---------------"
                print biosubclass
                print profile_updates
                getrsp = ucs.SetManagedObject(None, biosubclass, params=profile_updates)



    profile_updates = {}
    for param, desiredParamValue in desired_profile_params.iteritems():
        currParamValue = curr_profile_params[param]
        if param == "Count" or param == "RingSize":
            currParamValue = int(currParamValue)
            desiredParamValue = int(desiredParamValue)
        print "%s current value: [%s] desired value: [%s]" %(param, currParamValue, desiredParamValue)
        if currParamValue != desiredParamValue:
            profile_updates[param] = desiredParamValue

    if (len(profile_updates)>0):
        if (modify_requested_flag == 'True'):
            ucs.set_imc_managedobject(profile_res, params=profile_updates)
        return True
    else:
        return False


parser = argparse.ArgumentParser(description='Configure bios policy for ucsm')
parser.add_argument('-y', '--yamlfile', dest='yamlfile',
   default="ucs.yml",
   type=argparse.FileType('r'),
   help='YAML config file for ucs settings')
parser.add_argument('-i', '--ip', dest='ip',
   help='IP of the target CIMC')
parser.add_argument('-u', '--username', dest='username', default='admin',
   help='Username for login')
parser.add_argument('-p', '--password', dest='password', default='',
   help='Password for the user')
parser.add_argument('-c', '--reallymakechange', dest='modify', default='False',
   help='BIOS policy name to modify True/False')

try:
   ucs = Handle()
   ucs.Login(args.ip, args.username, args.password)
except Exception as e:
   print e
   exit(1)

classload = yaml.load(args.yamlfile)

print "Time to iterate through the yaml.
for classid, c-settings in classload.iteritems():
	print classid
        print c-setings
        
