#!/usr/bin/env python

# Get/Set cimc hostname on the servers via the api

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

	print "get the hostname "
	pwstatus = ucs.get_imc_managedobject(None, params={'Dn': 'sys/rack-unit-1/mgmt/if-1'})[0]
	print pwstatus
#	status1 = ucs.set_imc_managedobject(pwstatus, class_id="CommSyslogClient", params={'Dn': 'sys/svc-ext/syslog/client-primary','adminState': 'enabled', 'hostname': '10.114.214.4'})
#	pwstatus = ucs.get_imc_managedobject(None, params={'Dn': 'sys/svc-ext/syslog/client-primary'})[0]
#	print pwstatus

        ucs.logout()

# Do I really care what they are set to? I want to overwrite
        # Retrieve the VLAN/ethernet settings for the vNIC
#        	iface_vlan_res = ucs.GetImcManagedObject(None,
#                	params={'Dn': "%s/general" % iface_dn})
#        # Convert the results to dictionaries
#        	adapter_iface = iface_res[0].__dict__
#        	adapter_iface_vlan = iface_vlan_res[0].__dict__
#
#        # Validate current settings
#        	if adapter_iface['UplinkPort'] != values[eth]['uplink_port']:
#            		iface_updates['UplinkPort'] = values[eth]['uplink_port']
#        	if adapter_iface['PxeBoot'] != values[eth]['pxe']:
#            		iface_updates['PxeBoot'] = values[eth]['pxe']
#        	if adapter_iface_vlan['VlanMode'] != values[eth]['vlan_mode'].upper():
#            		vlan_updates['VlanMode'] = values[eth]['vlan_mode'].upper()
#
## Again I want to force the vlan id
#        	if 'vlan_id' in values[eth].keys():
#            		vlan_updates['Vlan'] = values[eth]['vlan_id']
#
#        # Commit any interfaces changes
#        	if iface_updates:
#            		print "Updating %s interface settings" % iface
#            		ucs.SetImcManagedObject(iface_res, params=iface_updates)
#            		reset = True
#        # Commit any VLAN changes
#        	if vlan_updates:
#            		print "Updating %s interface VLAN settings" % iface
#            		ucs.SetImcManagedObject(iface_vlan_res, params=vlan_updates)
#            		reset = True
#
#    # Notify the user if they should reset the system
#    if reset and args.reboot:
#	print "You used -r so we will reboot now for setting to take effect"
#	pwstatus = ucs.GetImcManagedObject(None, params={'Dn': 'sys/rack-unit-1'})
#	status1 = ucs.SetImcManagedObject(pwstatus, params={'AdminPower': 'cycle-immediate'})
#    elif reset:
#        print "Must reset %s for changes to apply" % args.ip
#
#    # Close the session

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configure vNICs for CIMC')
    parser.add_argument('-f', '--file', dest='hostfile',
                       help='List of Hosts to Modify')
    parser.add_argument('-p', '--password', dest='password', default='',
                       help='Password for the user')
    args = parser.parse_args()

    main(args)
