#!/usr/bin/env python

# clear the sel log

from ImcSdk import *
import argparse
import yaml

def main(args):
    reset = False

#    open file and start loop  
    for hosts in open (args.hostfile): 
	print hosts.rstrip()
    # Login to the UCS
    	try:
		ucs = ImcHandle()
	        ucs.login(hosts.rstrip(), "admin", args.password)
        except Exception as e:
       		print e
	        exit(1)

	print "get the syslog config"
	celstatus = ucs.get_imc_managedobject(None, params={'Dn': 'sys/rack-unit-1/mgmt/log-SEL-0'})[0]
	print celstatus
	status1 = ucs.set_imc_managedobject(celstatus, class_id="SysdebugMEpLog", params={'DN': 'sys/rack-unit-1/mgmt/log-SEL-0', 'adminState': 'clear', 'type': 'SEL'})


	celstatus = ucs.get_imc_managedobject(None, params={'Dn': 'sys/rack-unit-1/mgmt/log-SEL-0'})[0]
	print celstatus

        ucs.logout()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configure vNICs for CIMC')
    parser.add_argument('-f', '--file', dest='hostfile',
                       help='List of Hosts to Modify')
    parser.add_argument('-p', '--password', dest='password', default='',
                       help='Password for the user')
    args = parser.parse_args()

    main(args)
