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
                    help='Hostname')
parser.add_argument('-p', dest='password', action='store',
                    help='Admin Password')
parser.add_argument('-a', dest='adaptprofile', action='store',
                    help='Adapter Profile Name')


args = parser.parse_args()

if not args.adaptprofile:
#        args.adaptprofile = 'TX_RX_OffLoadOff'
        args.adaptprofile = 'linux-8rxtx-noff'
        print "didn't give us a profile to look for so assume it's a %s" % args.adaptprofile

sys.exit

# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
#print "getRsp ---- "
#print getRsp
#print "getRsp ---- "
adapters = handle.GetManagedObject(None, AdaptorHostEthIfProfile.ClassId(), inHierarchical=False,)
#print adapters
for adapter in adapters:
	if adapter.Name == 'linux-8rxtx-noff':
#		print "adapter ----"
#		print adapter
#		print "adapter --- "
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
#
#
# Now want to create an adapter profile
# Add managed object. W
handle.Logout
