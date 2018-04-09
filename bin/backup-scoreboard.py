#!/usr/bin/env python
import xml
from xml.etree import ElementTree
import requests
from requests.auth import HTTPBasicAuth
import re
import datetime
import os
import ConfigParser
import getopt
import sys
import json
import csv

def usage():
    print "usage: backup-scoreboard.py [-jh]"
    print "    -j: create JSON formatted backup files in addition to default CSV"
    print "    -h: print this usage message"

try:
   opts, args = getopt.getopt(sys.argv[1:],"hj")
except getopt.GetoptError:
    usage()
    sys.exit(1)

WRITEJSON = False
for opt, arg in opts:
    if opt == '-h':
        usage()       
        sys.exit()
    elif opt == '-j':
        WRITEJSON = True

SPLUNK_HOME = os.environ['SPLUNK_HOME']

CONF_FILE = "%s/etc/apps/SA-ctf_scoreboard_admin/bin/backuprestore.config" % SPLUNK_HOME

Config = ConfigParser.ConfigParser()
parsed_conf_files = Config.read(CONF_FILE)
if not CONF_FILE in parsed_conf_files:
    print "Could not read or parse config file (%s)" % CONF_FILE
    sys.exit(1)

SCHEME = Config.get('BackupRestore', 'SCHEME')
HOST = Config.get('BackupRestore', 'HOST')
PORT = Config.get('BackupRestore', 'PORT')
USER = Config.get('BackupRestore', 'USER')
PASS = Config.get('BackupRestore', 'PASS')
VERIFYCERT = Config.getboolean('BackupRestore', 'VERIFYCERT')
BACKUPDIR = Config.get('BackupRestore', 'BACKUPDIR')

APPS = ['SA-ctf_scoreboard', 'SA-ctf_scoreboard_admin']
BLACKLIST = ['SavedSearchHistory', 'user_realnames', 'ta_builder_meta_collection', \
'SearchHeadClusterHealthStates', 'SamlIdpCerts', 'SearchHeadClusterMemberInfo']

now = datetime.datetime.now()
nowstr = now.strftime('%Y%m%d%H%M%S')
basepath = BACKUPDIR + '/' + nowstr

if not os.path.exists(basepath):
    os.makedirs(basepath)

for app in APPS:
    print
    print app
    print "---------------------"
    apppath = basepath + '/' + app
    if not os.path.exists(apppath):
        os.makedirs(apppath)
    
    LISTENDPOINT = '/servicesNS/nobody/' + app + '/storage/collections/config'
    DATAENDPOINT = '/servicesNS/nobody/' + app + '/storage/collections/data/'

    url = SCHEME + '://' + HOST + ':' + str(PORT) + LISTENDPOINT
    response = requests.get(url, auth=HTTPBasicAuth(USER, PASS), verify=VERIFYCERT)

    tree = ""
    tree = ElementTree.fromstring(response.content)
    entries = []
    for elem in tree:
        if re.search('entry$', elem.tag):
            tempdict = {}
            tempdict['dobackup'] = 0
            for entryelement in elem:
                if re.search('title$', entryelement.tag):
                    tempdict['title'] = entryelement.text
                if re.search('id$', entryelement.tag):
                    if re.search(app, entryelement.text):
                        tempdict['dobackup'] = 1 
            entries.append(tempdict)

    for entry in entries:
        if entry['dobackup'] == 1 and not entry['title'] in BLACKLIST:
            print entry['title']
            url = SCHEME + '://' + HOST + ':' + str(PORT) + DATAENDPOINT + entry['title']
            response = requests.get(url, auth=HTTPBasicAuth(USER, PASS), verify=VERIFYCERT)
            print response
            responsearray = json.loads(response.content)
            keys = responsearray[0].keys()
            with open(apppath + '/' + entry['title'] + '.csv', 'w') as csv_file:
                dict_writer = csv.DictWriter(csv_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(responsearray)

            if WRITEJSON:
                fo = open(apppath + '/' + entry['title'] + '.json', 'w')
                fo.write (response.content)


