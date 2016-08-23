#!/usr/bin/env python

# To merge with existing ucs config: ./import-backup-xml-tmpl.py -H $ucs -f $ucs_tmpl_xml_file -u admin -p $ucs_password

# To Replace existing ucs config with imported ucs xml template: ./import-backup-xml-tmpl.py -H $ucs -f $ucs_tmpl_xml_file -u admin -p $ucs_password -m False

VERSION="%prog 1.0"

from UcsSdk import *
import argparse
import sys, traceback
import logging

defaultUserName = "admin"
defaultPassword = "password"
defaultMergeChoice = "True"

def main():
    handle = UcsHandle()
    
    try:
        parser = argparse.ArgumentParser(description='UCS import backup xml script')
        parser.add_argument('-H', '--host', help='UCS server name or IP address', required=True)
        parser.add_argument('-u', '--username', help='login user name')
        parser.add_argument('-p', '--password', help='login password')
        args = vars(parser.parse_args())

        if not args['host']:
            parser.print_help()
            parser.error("No <host> defined!")
            exit(3)

        ucspod = args['host']
        print "ucspod name: <%s>" %(ucspod)

        username = defaultUserName
        if args['username']:
            username = args['username']
      
        password = defaultPassword
        if args['password']:
            password= args['password']

             
        handle.Login(ucspod, username, password)
        imagePath1 = r"/Users/lwatta/Downloads/ucs-k9-bundle-b-series.2.2.5a.B.bin"
        handle.SendUcsFirmware(path=imagePath1)
        imagePath2 = r"/Users/lwatta/Downloads/ucs-k9-bundle-c-series.2.2.5a.C.bin"
        handle.SendUcsFirmware(path=imagePath2)
        imagePath3 = r"/Users/lwatta/Downloads/ucs-k9-bundle-infra.2.2.5a.A.bin"
        handle.SendUcsFirmware(path=imagePath3)
        handle.Logout()

    except SystemExit, e:
            sys.exit(e)

    except Exception, err:
            handle.Logout()
            print "Exception:", str(err)
            import traceback, sys
            print '-'*60
            traceback.print_exc(file=sys.stdout)
            print '-'*60

if __name__ =='__main__':
    main()
