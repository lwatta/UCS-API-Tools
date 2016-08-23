#!/usr/bin/env python

DOCUMENTATION = '''
---
module: UCSM_generic_yaml_update
version_added: 0.1
short_description: UCSM_generic_yaml_update updates single level items based off input yml file
description: Generic UCS yaml updater
author: lwatta
'''


from UcsSdk import *
import argparse
import yaml
import json

EXAMPLES = '''
Examples
'''


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

### ---------------------------------------------------------------------------
### MAIN
### ---------------------------------------------------------------------------

def main():
  module = AnsibleModule(
    argument_spec = dict(
      ucsm_ip=dict(required=True),
      ucsm_user=dict(required=False),
      ucsm_pw=dict(required=True),
      yamlinput=dict(required=True),
      override=dict(required=False, default=False),
      logfile=dict(required=False, default=None),
      timeout=dict(required=False, default=0)
    ),
    supports_check_mode = False
  )

def UCSM_generic_yaml_update(module):
    try:
       ucs = UcsHandle()
       ucs.Login(module.params['ucsm_ip],module.params['ucs_user'], module.params['ucsm_pw'])
    except 
        module.fail_json(msg="Could not login to UCSM cause we suck")

#    print "Time to iterate through the yaml"

    ucsclassload = yaml.load(args.config)
     depth = dict_depth(ucsclassload)
#     print depth

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

        
