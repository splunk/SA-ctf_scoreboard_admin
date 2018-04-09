#!/usr/bin/env python2.7
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
    print "usage: restore-scoreboard.py [-h] [-j] -d <backupdir>"
    print "    -j: restore from JSON formatted backup files instead of default CSV"
    print "    -h: print this usage message"
    print "    -d <backupdir>: specify the backup directory to restore from"


try:
   opts, args = getopt.getopt(sys.argv[1:],"d:hj")
except getopt.GetoptError:
    usage()
    sys.exit(1)

USEJSON = False
backupdir = ''
for opt, arg in opts:
    if opt == '-h':
        usage()       
        sys.exit()
    elif opt == '-j':
        USEJSON = True
    elif opt == '-d':
        backupdir = arg

if backupdir == '':
    usage()
    sys.exit(1)    

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

APPS = ['SA-ctf_scoreboard', 'SA-ctf_scoreboard_admin']
BLACKLIST = ['SavedSearchHistory', 'user_realnames', 'ta_builder_meta_collection', 'SearchHeadClusterHealthStates']




for app in APPS:

    filestorestore = {}

    for afile in os.listdir(backupdir + '/' + app):
        if USEJSON:
            if afile.endswith(".json"):
                collname = afile.replace('.json','')
                filestorestore[collname] = (backupdir + '/' + app + '/' + afile)
        else:
            if afile.endswith(".csv"):
                collname = afile.replace('.csv','')
                filestorestore[collname] = (backupdir + '/' + app + '/' + afile)


    for collname in filestorestore:
        print  "Preparing to restore collection " + collname + " from file: " + filestorestore[collname]

    print "Querying splunk for a list of existing KV store collections."

    LISTENDPOINT = '/servicesNS/nobody/' + app + '/storage/collections/config'
    DATAENDPOINT = '/servicesNS/nobody/' + app + '/storage/collections/data/'

    url = SCHEME + '://' + HOST + ':' + str(PORT) + LISTENDPOINT
    response = requests.get(url, auth=HTTPBasicAuth(USER, PASS), verify=VERIFYCERT)

    print response

    tree = ElementTree.fromstring(response.content)
    entries = []
    for elem in tree:
        if re.search('entry$', elem.tag):
            tempdict = {}
            for entryelement in elem:
                if re.search('title$', entryelement.tag):
                    tempdict['title'] = entryelement.text
            entries.append(tempdict)

    for entry in entries:
        if entry['title'] in filestorestore:
            if not entry['title'] in BLACKLIST:
                print "Splunk has a KV store collection named: " + entry['title'] +  "  Attempting to restore file " + filestorestore[entry['title']] + "..."
                print "  Removing entries from collection: " + entry['title']
                url = SCHEME + '://' + HOST + ':' + str(PORT) + DATAENDPOINT + entry['title']
                response = requests.delete(url, auth=HTTPBasicAuth(USER, PASS), verify=VERIFYCERT)
                print "  Restoring entries to collection: " + entry['title']
                url = SCHEME + '://' + HOST + ':' + str(PORT) + DATAENDPOINT + entry['title'] + "/batch_save"
                headers = {'Content-Type' : 'application/json'}

                if USEJSON:
                    response = requests.post(url, auth=HTTPBasicAuth(USER, PASS), verify=VERIFYCERT, data=open(filestorestore[entry['title']], 'rb'), headers=headers)
                else:
                    with open(filestorestore[entry['title']], 'rb') as csv_file:
                        dict_reader = csv.DictReader(csv_file)
                        csvrows = []
                        for row in dict_reader:
                            csvrows.append(row)
                        data = json.dumps(csvrows)
                    response = requests.post(url, auth=HTTPBasicAuth(USER, PASS), verify=VERIFYCERT, data=data, headers=headers)

    print
