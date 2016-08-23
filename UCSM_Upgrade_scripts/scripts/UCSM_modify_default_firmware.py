#!/usr/bin/env python


# Purpose: Will modify the default firmware to the latest version

# Outline
#	login
#	check the args to either turn it on or turn it off
#	Do the action



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
parser = argparse.ArgumentParser(description='Turns callhome on or off. You need to supply the UCS system, password and action. If no action then it just shows the current status')
parser.add_argument('-u', dest='ucshostname', action='store',
                    help='UCS Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')
parser.add_argument('-a', dest='upordown', action='store',
                    help='Optional {on/off}')


args = parser.parse_args()

# Login first
handle = UcsHandle()
handle.Login(args.ucshostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, FirmwareComputeHostPack.ClassId(), {FirmwareComputeHostPack.NAME: "default"})
print getRsp[0]
handle.SetManagedObject(getRsp[0],FirmwareComputeHostPack.ClassId(),{FirmwareComputeHostPack.DN: getRsp[0].Dn, FirmwareComputeHostPack.BLADE_BUNDLE_VERSION: "2.2(5a)B", FirmwareComputeHostPack.RACK_BUNDLE_VERSION: "2.2(5a)C"})

getRsp = handle.GetManagedObject(None, FirmwareComputeHostPack.ClassId(), {FirmwareComputeHostPack.NAME: "default"})
print getRsp[0]
handle.Logout
sys.exit(0)


