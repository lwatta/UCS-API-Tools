#!/usr/bin/python


# Purpose: Create server pools in Nimbus for Rack and Blades
#	This way we can simply create needed SPs and not worry about actually allocating them
#	against free servers
#
# Outline
#	login
#	Create ServerPool "CCSBlades" and "CCSRacks" and "CCSRacksBigData"



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


args = parser.parse_args()

def ucs_create_serverpool(handle, obj, poolname):
	print "Pool to create is %s" % poolname
 
	

# Login first
handle = UcsHandle()
handle.Login(args.hostname, "admin", args.password)
getRsp = handle.GetManagedObject(None, OrgOrg.ClassId(),{OrgOrg.DN: "org-root"})[0]
#print "getRsp ---- "
#print getRsp
#print "getRsp ---- "
template = {}
# Get Service Profiles
# Create blades
#addRsp= handle.AddManagedObject(getRsp, ComputePool.ClassId(), {"ComputePool.NAME":"CCSBlades"}, True)
#ucs_create_serverpool(handle, getRsp, "CCSBlades")

#Commands that work
addRsp= handle.AddManagedObject(None, ComputePool.ClassId(), { ComputePool.DN:"org-root",ComputePool.NAME:"CCSBlades"}, True)

print "nova1"

addRsp= handle.AddManagedObject(None, ComputeQual.ClassId(), { ComputeQual.DN:"org-root",ComputeQual.NAME:"CCSBladesPolicy"}, True)
addRspQual=handle.AddManagedObject(addRsp, ComputeChassisQual.ClassId(), {ComputeChassisQual.MAX_ID:"20",ComputeChassisQual.MIN_ID:"1"})

addRsp= handle.AddManagedObject(None, ComputePoolingPolicy.ClassId(), { ComputePoolingPolicy.DN:"org-root",ComputePoolingPolicy.NAME:"CCSBladesPoolPol",ComputePoolingPolicy.QUALIFIER:"CCSBladesPolicy",ComputePoolingPolicy.POOL_DN:"org-root/compute-pool-CCSBlades"}, True)

#nova2 nodes
addRsp= handle.AddManagedObject(None, ComputePool.ClassId(), { ComputePool.DN:"org-root",ComputePool.NAME:"CCSRackNova2-Pool"}, True)

print "nova2"

addRsp= handle.AddManagedObject(None, ComputeQual.ClassId(), { ComputeQual.DN:"org-root",ComputeQual.NAME:"CCSRackNova2-Q"}, True)
addRspQual=handle.AddManagedObject(addRsp, ComputePhysicalQual.ClassId(), {ComputePhysicalQual.MODEL:"UCSC-C220"})

addRsp= handle.AddManagedObject(None, ComputePoolingPolicy.ClassId(), { ComputePoolingPolicy.DN:"org-root",ComputePoolingPolicy.NAME:"CCSRackNova2-Pol",ComputePoolingPolicy.QUALIFIER:"CCSRackNova2-Q",ComputePoolingPolicy.POOL_DN:"org-root/compute-pool-CCSRackNova2-Pool"}, True)

#nova3 nodes
addRsp= handle.AddManagedObject(None, ComputePool.ClassId(), { ComputePool.DN:"org-root",ComputePool.NAME:"CCSRackNova3-Pool"}, True)

print "nova3"

addRsp= handle.AddManagedObject(None, ComputeQual.ClassId(), { ComputeQual.DN:"org-root",ComputeQual.NAME:"CCSRackNova3-Q"}, True)
addRspQual=handle.AddManagedObject(addRsp, ComputePhysicalQual.ClassId(), {ComputePhysicalQual.MODEL:"UCSC-C240"})

addRsp= handle.AddManagedObject(None, ComputePoolingPolicy.ClassId(), { ComputePoolingPolicy.DN:"org-root",ComputePoolingPolicy.NAME:"CCSRackNova3-Pol",ComputePoolingPolicy.QUALIFIER:"CCSRackNova3-Q",ComputePoolingPolicy.POOL_DN:"org-root/compute-pool-CCSRackNova3-Pool"}, True)

handle.Logout
