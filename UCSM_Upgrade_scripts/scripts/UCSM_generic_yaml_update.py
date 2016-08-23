#!/usr/bin/env python

# Purpose: Take simple UCS information in yaml configuration and iterate through it making changes
# yaml config should take a classid and then settings that should be changed.
# including DN in the yaml file
# won't work for all UCS configs as some things require additional processing. This is mean for simple changes
# 	much like the CIMC settings for standalone.

from UcsSdk import *
import argparse
import yaml
#import ssl
#ssl._create_default_https_context=ssl._create_unverified_context

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

def checkAndModifyProfileD2(ucs, classid, desired_settings, modify_requested_flag):
    profile_res = ucs.GetManagedObject(None, classid, None, inHierarchical=True)
    curr_class = profile_res[0].__dict__
    profile_updates = {}
    for subvaluekey, subvalueitem in desired_settings.iteritems():
        print subvaluekey
        print subvalueitem
        print curr_class["classId"]
        curr_value = curr_class[subvaluekey]
        print "%s current value: [%s] desired value: [%s]" %(subvaluekey, curr_value, subvalueitem)
        profile_updates[subvaluekey] = subvalueitem
        if (modify_requested_flag == 'True'):
            print "-------------- make change ---------------"
            print subvaluekey
            print subvalueitem
            getrsp = ucs.SetManagedObject(None, classid, params=profile_updates)
 
def dict_depth(d, depth=0):
    if not isinstance(d, dict) or not d:
        return depth
    return max(dict_depth(v, depth+1) for k, v in d.iteritems())

parser = argparse.ArgumentParser(description='Configure yaml policies for ucsm')
parser.add_argument('-b', '--cfg', dest='config',
   default="bios.yml",
   type=argparse.FileType('r'),
   help='YAML config file for ovs vNIC specific setting')
parser.add_argument('-i', '--ip', dest='ip',
   help='IP of the target CIMC')
parser.add_argument('-u', '--username', dest='username', default='admin',
   help='Username for login')
parser.add_argument('-p', '--password', dest='password', default='',
   help='Password for the user')
parser.add_argument('-c', '--reallymakechange', dest='modify', default='False',
   help='BIOS policy name to modify True/False')

args = parser.parse_args()
try:
   ucs = UcsHandle()
   ucs.Login(args.ip, args.username, args.password)
except Exception as e:
   print e
   exit(1)

print "Time to iterate through the yaml"

ucsclassload = yaml.load(args.config)
depth = dict_depth(ucsclassload)
print depth

if depth == 2:
    for classid, csettings in ucsclassload.iteritems():
        print classid
        print "Length %d" % len(csettings)
        checkAndModifyProfileD2(ucs, classid, csettings, args.modify)
else:
        print classid
        print "Length %d" % len(csettings)
        checkAndModifyProfile(ucs, classid, csettings, args.modify)

        
ucs.Logout()
