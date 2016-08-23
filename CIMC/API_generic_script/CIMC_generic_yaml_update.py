#!/usr/bin/env python

# Purpose: Take simple UCS information in yaml configuration and iterate through it making changes
# yaml config should take a classid and DN nd then settings that should be changed.
# including DN in the yaml file
# won't work for all UCS configs as some things require additional processing. This is mean for simple changes
# 	much like the CIMC settings for standalone.

# To make it faster lets check for things we know won't exist and just shotgun everything else.
#	This will remove the painful need to get every object and check it.
#	If the classid is not one of the special types that need to be checked we will just make the settings.


from ImcSdk import *
import argparse
# we use raumel.yaml instead of just yaml because it can read the yaml file and give it back to
#	us in the order in which its in the the file. This is important because have some settings
#	require objects to be created first before other operations can be performed.

import ruamel.yaml as yaml
#import yaml

# SSL Passthrough Fix
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context

# quick and dirty set whats in the dict. Don't check just set it.
def ModifyProfileD2(ucs, classid, desired_settings,  modify_requested_flag):
    if (modify_requested_flag == 'True'):
       print "-------------- make change ---------------"
       print desired_settings
       getrsp = ucs.set_imc_managedobject(None, classid, params=desired_settings)
       if not getrsp:
	  print "No Class or params for %s" % classid
	  print "Check your yaml config against the CIMC object model"
    else:
       print "-------------- No change ---------------"
# this is only if we are checking data if modify is not true
       profile_res = ucs.get_imc_managedobject(None, classid, params={'Dn': desired_settings['Dn']})
       if not profile_res:
	  print "No Class or params for %s" % classid
	  print "Check your yaml config against the CIMC object model"
       else:
          curr_class = profile_res[0].__dict__
          profile_updates = {}
          for subvaluekey, subvalueitem in desired_settings.iteritems():
             curr_value = curr_class[subvaluekey]
             print "%s current value: [%s] desired value: [%s]" %(subvaluekey, curr_value, subvalueitem)


# We always assume for this function that Dn is one of the values in the DICT.
# if its not then we are fucked :)
# Note: Right now this is not a check. We are just setting the vars regardless of what is there.
#	We are not trying to compare. should probaly do a compare to make things faster :)

def checkAndModifyProfileD2(ucs, classid, desired_settings, modify_requested_flag):
    print "-------------- Checking  ---------------"
    profile_res = ucs.get_imc_managedobject(None, classid, params={'Dn': desired_settings['Dn']})
    if not profile_res:
       print "Dn %s does not exist" % desired_settings['Dn']
# this should be a simple call like
       if (modify_requested_flag == 'True'):
          print "-------------- Creating  ---------------"
          getrsp = ucs.add_imc_managedobject(None,classid, params=desired_settings)
	  if not getrsp:
	     print "Could not add Classid %s " % classid
    else:
       print "Dn %s does exist" % desired_settings['Dn']
       curr_class = profile_res[0].__dict__
#    print desired_settings['Dn']
       profile_updates = {}

       for subvaluekey, subvalueitem in desired_settings.iteritems():
#        print curr_class['_class_id']
# in the future we should check here to see if settings are already set. but for now shotgun!
          curr_value = curr_class[subvaluekey]
          print "%s current value: [%s] desired value: [%s]" %(subvaluekey, curr_value, subvalueitem)
          profile_updates[subvaluekey] = subvalueitem

       print profile_updates
       if (modify_requested_flag == 'True'):
           print "-------------- make change ---------------"
           getrsp = ucs.set_imc_managedobject(None, classid, params=profile_updates)

def dict_depth(d, depth=0):
    if not isinstance(d, dict) or not d:
        return depth
    return max(dict_depth(v, depth+1) for k, v in d.iteritems())

parser = argparse.ArgumentParser(description='Configure yaml policies for ucsm')
parser.add_argument('-b', '--cfg', dest='config',
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

ucsclassload = yaml.load_all(args.config, yaml.RoundTripLoader)
#ucsclassload = yaml.load(args.config)
#depth = dict_depth(ucsclassload)
#print "depth ----"
#print depth


try:
   ucs = ImcHandle()
   ucs.login(args.ip, args.username, args.password)
except Exception as e:
   print e
   exit(1)

print "Time to iterate through the yaml"
checkrequired = ['Adaptor', 'Lsboot']
docheck = 0

for docs in ucsclassload:
   for classid, csettings in docs.iteritems():
#       print classid
#       print csettings['Dn']
#      print "Length %d" % len(csettings)
       for i in checkrequired:
          if i in classid:
             docheck = 1

       if docheck == 1:
#          print "Check"
          checkAndModifyProfileD2(ucs, classid, csettings, args.modify)
       else:
#          print "No Check"
          ModifyProfileD2(ucs, classid, csettings, args.modify)
       docheck = 0

ucs.logout()
