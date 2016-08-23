#!/usr/bin/env python

# Copyright 2013 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script downloads the Tech Support file from UCS Manager.
# Usage: downloadTechSupportFile.py [options]
#
# Options:
# -h, --help            show this help message and exit
# -i IP, --ip=IP        [Mandatory] UCSM IP Address
# -u USERNAME, --username=USERNAME
#                       [Mandatory] Account Username for UCSM Login
# -p PASSWORD, --password=PASSWORD
#                       [Mandatory] Account Password for UCSM Login
# -f PATHPATTERN, --pathPattern=PATHPATTERN
#                       [Mandatory] Complete path(with file name) for
#                       TechSupport backup
#
# Note : File extension must be ".tar".
# Please refer Quick Start Guide for other parameter sets.

import getpass
import optparse
from UcsSdk import *

def getpassword(prompt):
	if platform.system() == "Linux":
		return getpass.unix_getpass(prompt=prompt)
	elif platform.system() == "Windows" or platform.system() == "Microsoft":
		return getpass.win_getpass(prompt=prompt)
	else:
		return getpass.getpass(prompt=prompt)

if __name__ == "__main__":
	handle = UcsHandle()
	try:
		parser = optparse.OptionParser()
		parser.add_option('-i', '--ip',dest="ip",
      					help="[Mandatory] UCSM IP Address")
		parser.add_option('-u', '--username',dest="userName",
      					help="[Mandatory] Account Username for UCSM Login")
		parser.add_option('-p', '--password',dest="password",
      					help="[Mandatory] Account Password for UCSM Login")
		parser.add_option('-f', '--pathPattern',dest="pathPattern",
						help="[Mandatory] Complete path(with file name) for \
TechSupport backup")
				
		(options, args) = parser.parse_args()
		
		if not options.ip:
			parser.print_help()
			parser.error("Provide UCSM IP Address")
		if not options.userName:
			parser.print_help()
			parser.error("Provide UCSM UserName")
		if not options.password:
			options.password=getpassword("UCSM Password:")
		if not options.pathPattern:
			parser.print_help()
			parser.error("Provide pathPattern. e.g. \
C:/TechSupport_Backups/techsupp_ucsm.tar")
			
		handle.Login(options.ip,options.userName,options.password)
		
		handle.GetTechSupport(pathPattern= options.pathPattern , 
							ucsManager=True)
		handle.Logout()

	except Exception, err:
		handle.Logout()
		print "Exception:", str(err)
		import traceback, sys
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60

