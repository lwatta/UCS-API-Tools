#!/usr/bin/python

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

parser = argparse.ArgumentParser(description='Script to make sure Nova and Net SPs are associated to an updating template')
parser.add_argument('-u', dest='hostname', action='store',
                    help='UCSM Hostname or IP')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password for UCSM')
parser.add_argument('-a', dest='adaptprofile', action='store', default='TX_RX_OffLoadOff',
                    help='Adapter Profile Name. Default is TX_RX_OffLoadOff')
parser.add_argument('-l', dest='givemelist', action='store_true',
                    help='Give me a list of all the adapters')


args = parser.parse_args()

if args.givemelist:
	print "Here is a lit of all adapterprofiles"

# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
adapters = handle.GetManagedObject(None, AdaptorHostEthIfProfile.ClassId(), inHierarchical=False,)

for adapter in adapters:
	if (not args.givemelist and adapter.Name == args.adaptprofile):
		childs = handle.GetManagedObject(None, AdaptorHostEthIfProfile.ClassId(), {AdaptorHostEthIfProfile.DN: adapter.Dn} , inHierarchical=True)
		print adapter.Dn
		for child in childs:
			if child.Rn == "eth-offload":
				print "TX Checksum Offload ---------> %s --------> should be disabled" % child.TcpTxChecksum
				print "RX Checkum Offload ----------> %s --------> should be disabled" % child.TcpRxChecksum
				print "TCP Large Receive Offload ---> %s --------> should be disabled" % child.LargeReceive
				print "TCP Segmentation Offload ----> %s --------> should be disabled" % child.TcpSegment
			elif child.Rn == "eth-rcv-q":
				print "Receive Queues --------------> %s --------> should be 8" % child.Count
				print "Receive Ring Size -----------> %s --------> should be 1024" % child.RingSize
			elif child.Rn == "eth-work-q":
				print "Transmit Queues -------------> %s --------> should be 8" % child.Count
				print "Transmit Ring Size ----------> %s --------> should be 1024" % child.RingSize
			elif child.Rn == "eth-comp-q":
				print "Completion Queues -----------> %s --------> should be 16" % child.Count
			elif child.Rn == "rss":
				print "RSS -------------------------> %s -------------> should be enabled" % child.ReceiveSideScaling
			elif child.Rn == "eth-int":
				print "Interrupts ------------------> %s --------> should be 18" % child.Count
	elif args.givemelist:
		print adapter.Name
#
#
# Now want to create an adapter profile
# Add managed object. W
handle.Logout
