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

# This script takes the back up of UCS Manager Configuration.
# Usage: backupUcsManager.py [options]
#
# Options:
# -h, --help            show this help message and exit
# -i IP, --ip=IP        [Mandatory] UCSM IP Address
# -u USERNAME, --username=USERNAME
#                       [Mandatory] Account Username for UCSM Login
# -p PASSWORD, --password=PASSWORD
#                       [Mandatory] Account Password for UCSM Login
# -t TYPE, --type=TYPE  [Mandatory] Backup type
# -f PATHPATTERN, --pathPattern=PATHPATTERN
#                       [Mandatory] Complete path(with file name) for backup
#
# Note : For "full-state" backup file name extension must be ".tar.gz" and 
# for others ".xml"

import getpass
import optparse
import platform
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
		parser.add_option('-t', '--type',dest="type",
                          help="[Mandatory] Backup type")
		parser.add_option('-f', '--pathPattern',dest="pathPattern",
              help="[Mandatory] Complete path(with file name) for backup")
				
		(options, args) = parser.parse_args()
		
		if not options.ip:
			parser.print_help()
			parser.error("Provide UCSM IP Address")
		if not options.userName:
			parser.print_help()
			parser.error("Provide UCSM UserName")
		if not options.password:
			options.password=getpassword("UCSM Password:")
		if not options.type:
			parser.print_help()
			parser.error("Provide backup type [full-state, config-logical, \
config-system, config-all]")
		if not options.pathPattern:
			parser.print_help()
			parser.error("Provide pathPattern. e.g. \
C:/Backups/configlogical.xml")
			
		handle.Login(options.ip,options.userName,options.password)
		
		handle.BackupUcs(type=options.type, pathPattern=options.pathPattern)
		handle.Logout()

	except Exception, err:
		handle.Logout()
		print "Exception:", str(err)
		import traceback, sys
		print '-'*60
		traceback.print_exc(file=sys.stdout)
		print '-'*60

