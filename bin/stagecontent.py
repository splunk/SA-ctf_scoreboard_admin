#!/usr/bin/env python

import sys, time, urllib
from splunklib.searchcommands import \
    dispatch, GeneratingCommand, Configuration, Option, validators
from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path

@Configuration()
class StageContentCommand(GeneratingCommand):
    ctf_users_staged = Option(require=True)
    ctf_questions_staged = Option(require=True)
    ctf_answers_staged = Option(require=True)
    ctf_hints_staged = Option(require=True)

    LOOKUPS_DIR = make_splunkhome_path(['etc', 'apps', 'SA-ctf_scoreboard_admin', 'lookups'])

    def generate(self):
        urllib.urlretrieve(self.ctf_users_staged, "%s/%s" % (self.LOOKUPS_DIR, 'ctf_users_staged.csv'))
        yield {'_time': time.time(), '_raw': self.ctf_users_staged }

        urllib.urlretrieve(self.ctf_questions_staged, "%s/%s" % (self.LOOKUPS_DIR, 'ctf_questions_staged.csv'))
        yield {'_time': time.time(), '_raw': self.ctf_questions_staged }

        urllib.urlretrieve(self.ctf_answers_staged, "%s/%s" % (self.LOOKUPS_DIR, 'ctf_answers_staged.csv'))
        yield {'_time': time.time(), '_raw': self.ctf_answers_staged }

        urllib.urlretrieve(self.ctf_hints_staged, "%s/%s" % (self.LOOKUPS_DIR, 'ctf_hints_staged.csv'))
        yield {'_time': time.time(), '_raw': self.ctf_hints_staged }

dispatch(StageContentCommand, sys.argv, sys.stdin, sys.stdout, __name__)