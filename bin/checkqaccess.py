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
class checkQAccess(ReportingCommand):
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
        retrieveacl = myhttp.request(baseurl + '/servicesNS/nobody/SA-ctf_scoreboard/configs/conf-transforms/ctf_questions/acl?output_mode=json','GET', headers={'Authorization': 'Splunk %s' % session_key})[1]
        acldict=json.loads(retrieveacl)

        canread = False
        for reader in acldict['entry'][0]['acl']['perms']['read']:
            if reader == 'ctf_competitor':
                canread = True
        
        canwrite = False
        for writer in acldict['entry'][0]['acl']['perms']['write']:
            if writer == 'ctf_competitor':
                canwrite = True
        result = collections.OrderedDict({'role': 'ctf_competitor', 'canread': canread, 'canwrite': canwrite})
        
        resultstoreturn.append(result)
        return resultstoreturn
    
if __name__ == "__main__":
    dispatch(checkQAccess, sys.argv, sys.stdin, sys.stdout, __name__)