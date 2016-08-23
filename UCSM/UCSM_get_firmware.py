#!/usr/bin/python


# Purpose: get firmware for all systems
#
# Outline
#	login



# Import crap
import simplejson as json
import time
import datetime
import sys
import getopt
import getpass
import argparse
import re
from UcsSdk import *
from collections import defaultdict

# get login arguments
parser = argparse.ArgumentParser(description='Run single ucs api command to test something ')
parser.add_argument('-u', dest='inputfile', action='store',
                    help='File with list of UCS Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')


args = parser.parse_args()
for templine in open (args.inputfile).readlines():
    ucsnode = templine.split()

    handle = UcsHandle()
    handle.Login(ucsnode[0], "admin", args.password)
    obj = handle.GetManagedObject(None, "FirmwareInfra",params=None)[0]
    objb = handle.GetManagedObject(None, "FirmwareBlade",params=None)[0]
    objr = handle.GetManagedObject(None, "FirmwareRack",params=None)[0]
    print "%s,\t%s,\t%s,\t%s" % (ucsnode[0], obj.OperVersion, objb.OperVersion, objr.OperVersion)
    handle.Logout

print "----------------------------------------------------------------------------------------"

sys.exit(0)

