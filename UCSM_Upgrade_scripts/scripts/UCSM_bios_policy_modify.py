#!/usr/bin/env python

from UcsSdk import *
import argparse
import yaml
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context

# 10/8/15 lwatta
# adding an option where if no bios policy is given that the script will just loop through all bios policies
# 	and make the setttings.

def checkAndModifyProfile (ucs, classid, desired_settings, modify_requested_flag, passedname):
    profile_res = ucs.GetManagedObject(None, classid, {BiosVProfile.NAME : passedname }, inHierarchical=True)
    
    for biglist in profile_res:
        curr_class = biglist.__dict__
        for biosubclass, anotherdict in desired_settings.items():
#	    print curr_class["classId"]
            if biosubclass in curr_class["classId"]:
#                print "Change values -----------"
                profile_updates = {}
		for biosoption, value in anotherdict.iteritems():
			curr_value = getattr(biglist, biosoption)
                	print "%s current value: [%s] desired value: [%s]" %(biosoption, curr_value, value)
 			if "replace-me" in value:
#				print "found DN that needs replaement %s" % value
				dnpath = "bios-prof-" + passedname
				value= value.replace("replace-me",dnpath)
#				print value
			profile_updates[biosoption] = value
                if (modify_requested_flag == 'True'):
		       print "-------------- make change ---------------"
#		       print biosubclass
#  		       print profile_updates
                       getrsp = ucs.SetManagedObject(None, biosubclass, params=profile_updates)

parser = argparse.ArgumentParser(description='Configure bios policy for ucsm')
parser.add_argument('-b', '--bioscfg', dest='bconfig',
   default="bios.yml",
   type=argparse.FileType('r'),
   help='YAML config file for ovs vNIC specific setting')
parser.add_argument('-i', '--ip', dest='ip',
   help='IP of the target CIMC')
parser.add_argument('-u', '--username', dest='username', default='admin',
   help='Username for login')
parser.add_argument('-p', '--password', dest='password', default='',
   help='Password for the user')
parser.add_argument('-n', '--biospolicyname', dest='biospolicyname', default='',
   help='BIOS policy name to modify. Leave blank to modify all bios policies')
parser.add_argument('-c', '--reallymakechange', dest='modify', default='False',
   help='BIOS policy name to modify True/False')


args = parser.parse_args()

# Login to the UCS
try:
   ucs = UcsHandle()
   ucs.Login(args.ip, args.username, args.password)
except Exception as e:
   print e
   exit(1)
print "login done"
bioscfg = yaml.load(args.bconfig)

# remember to check that it exists and if it doesn't then fail
notfound = 0
getRsp = ucs.GetManagedObject(None,BiosVProfile.ClassId())
for biosprofile in getRsp:
      if args.biospolicyname and args.biospolicyname in biosprofile.Name:
	print "ok got the bios policy"
        notfound = 1
        for classid, desired_bios_settings in bioscfg.iteritems():
	    print classid
      	    checkAndModifyProfile(ucs, classid, desired_bios_settings, args.modify, args.biospolicyname)
      elif not args.biospolicyname:
        notfound = 1
        for classid, desired_bios_settings in bioscfg.iteritems():
	    print classid
      	    checkAndModifyProfile(ucs, classid, desired_bios_settings, args.modify, biosprofile.Name)
      else:
    	print "not found"

if notfound == 0:
    print "did not find bios policy in UCSM "
    sys.exit(1)

#for profile in bioscfg.iteritems():

ucs.Logout
