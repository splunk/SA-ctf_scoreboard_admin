#!/usr/bin/env python

from splunklib.searchcommands import dispatch, ReportingCommand, Configuration, Option, validators
import splunklib.results as results
import splunklib.client as client
from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path
import sys
import json
import time
import urllib
import httplib2
import re
from time import localtime,strftime
from xml.dom import minidom
import collections
import base64

@Configuration()
class toggleQAccess(ReportingCommand):
    @Configuration()
    def map(self, records):
        return records

    def reduce(self, records):
        '''
        Determine the Splunk user, session key, and app
        '''
        user = self._metadata.searchinfo.username
        session_key = self._metadata.searchinfo.session_key
        app = self._metadata.searchinfo.app

        resultstoreturn = []
        myhttp = httplib2.Http(disable_ssl_certificate_validation=True)
        baseurl = 'https://localhost:8089'

        # First retrieve current ACL
        retrieveacl = myhttp.request(baseurl + '/servicesNS/nobody/SA-ctf_scoreboard/configs/conf-transforms/ctf_questions/acl?output_mode=json','GET', headers={'Authorization': 'Splunk %s' % session_key})[1]
        acldict=json.loads(retrieveacl)

        readers=[]
        canread = False
        for reader in acldict['entry'][0]['acl']['perms']['read']:
            readers.append(reader)
            if reader == 'ctf_competitor':
                canread = True

        writers=[]
        canwrite = False
        for writer in acldict['entry'][0]['acl']['perms']['write']:
            writers.append(writer)
            if writer == 'ctf_competitor':
                canwrite = True
                
        # Toggle read access, always ensuring write access is disabled.

        if 'ctf_competitor' in readers:
            readers.remove('ctf_competitor')
        else:
            readers.append('ctf_competitor')

        if 'ctf_competitor' in writers:
            writers.remove('ctf_competitor')

        readersstring = ','.join(readers)
        writersstring = ','.join(writers)

        # Set the ACL
        setacl = myhttp.request(baseurl + '/servicesNS/nobody/SA-ctf_scoreboard/configs/conf-transforms/ctf_questions/acl?output_mode=json','POST', headers={'Authorization': 'Splunk %s' % session_key}, body=urllib.urlencode({"sharing" : "global","owner":"nobody",'perms.read': readersstring, 'perms.write':writersstring}))[1]
        acldict=json.loads(setacl)
        
        readers=[]
        canread = False
        for reader in acldict['entry'][0]['acl']['perms']['read']:
            readers.append(reader)
            if reader == 'ctf_competitor':
                canread = True
        writers=[]
        canwrite = False
        for writer in acldict['entry'][0]['acl']['perms']['write']:
            writers.append(writer)
            if writer == 'ctf_competitor':
                canwrite = True
        
        result = collections.OrderedDict({'role': 'ctf_competitor', 'canread': canread, 'canwrite': canwrite})
        resultstoreturn.append(result)
        return resultstoreturn
    
if __name__ == "__main__":
    dispatch(toggleQAccess, sys.argv, sys.stdin, sys.stdout, __name__)
