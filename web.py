#!/data/project/legobot/python/bin/python
"""
Copyright (C) 2013 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
print "Content-type: text/html\n\n"
import cgitb
cgitb.enable()
import cgi
import os
import requests
import subprocess
import hashlib
environ = {'INSTANCEPROJECT': 'tools',
           'LOGNAME': 'local-legobot',
           'USER': 'local-legobot',
           'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/X11R6/bin',
           'HOME': '/data/project/legobot/',
           'LANG': 'en_US.UTF-8',
           'TERM': 'xterm-256color',
           'SHELL': '/bin/bash',
           'SHLVL': '1',
           'PYWIKIBOT2_DIR': '/data/project/legobot/.pywikibot/',
           'SUDO_USER': 'legoktm',
           'USERNAME': 'local-legobot',
           'SUDO_UID': '2552',
           'INSTANCENAME': 'tools-login',
           '_': '/usr/bin/python',
           'SUDO_COMMAND': '/bin/bash',
           'SUDO_GID': '500',
           'OLDPWD': '/data/project/legobot/cgi-bin',
           'NODE_PATH': '/usr/lib/nodejs:/usr/share/javascript',
           'PWD': '/data/project/legobot/cgi-bin/massrename',
           'MAIL': '/var/mail/local-legobot',
           }


def TUSC(username, password, lang, project):
    headers = {'User-agent': 'Commons mass-rename tool by User:Legoktm'}
    # http://tools.wikimedia.de/~magnus/tusc.php?check=1&botmode=1&user=USERNAME&language=LANGUAGE&project=PROJECT&password=TUSC_PASSWORD
    params = {'check': 1,
              'botmode': 1,
              'user': username,
              'language': lang,
              'project': project,
              'password': password,
              }
    url = 'http://tools-webproxy/tusc/tusc.php'
    r = requests.post(url, params, headers=headers)
    try:
        if int(r.text) == 1:
            return True
    except Exception:
        pass
    return False


def authusers(username):
    with open(os.path.expanduser('~/.whitelist')) as f:
        t = f.read()
    for line in t:
        if line == username:
            return True
    return False


def wrap(thing):
    return '<html><head><title>The Super Rename Tool!</title></head><body>{0}</body></html>'.format(thing)


def start():
    form = """<form action="/legobot/cgi-bin/massrename/web.py" method="post">
        <input type="text" name="cat" placeholder="Category:Blah"><br />
        <input type="text" name="find" placeholder="Thing to find"><br />
        <input type="text" name="replace" placeholder="Thing to replace it with"><br />
        <input type="text" name="reason" placeholder="Move reason"><br />
        <input type="text" name="username" placeholder="TUSC: username"><br />
        <input type="password" name="password" placeholder="TUSC: password"><br />
        <input type="text" name="lang" placeholder="TUSC: language"><br />
        <input type="text" name="project" placeholder="TUSC: project"><br />

        <button type="submit">Go!</button>
      </form>
    """
    return wrap(form)


def tuscfailure():
    return wrap('Could not authenticate with TUSC.')


def notanadmin():
    return wrap('Unfortunately this tool can only be used by Commons administrators.')


def jobnotsent():
    return wrap('There was an error sending your job. Please contact Legoktm with details of what you were trying '
                'to do.')


def succeeded(val):
    return wrap('Your job has been sent. Legobot will process it shortly. If there are any issues, please let Legoktm '
                'know, and provide the ID for your job, which is: ' + val + '.')

form = cgi.FieldStorage()
if not 'cat' in form:
    print start()
    quit()

cat = form['cat'].value
username = form['username'].value
password = form['password'].value
lang = form['lang'].value
project = form['project'].value
find = form['find'].value
replace = form['replace'].value
reason = form['reason'].value
summary = reason + ". On behalf of " + username
t = TUSC(username, password, lang, project)
if not t:
    print tuscfailure()
    quit()
if not authusers(username):
    print notanadmin()
    quit()

h = hashlib.md5()
h.update(username)
h.update(cat)
h.update(find)
h.update(replace)
val = h.hexdigest()
#we all good?
#try:
x = subprocess.check_output('qsub -N {0} -l h_vmem=256M -j y -o $HOME/renamelogs/{0} /data/project/legobot/cgi-bin/massrename/rename.py "{1}" "{2}" "{3}" "{4}"'.format(
    val, cat, find, replace, summary), stderr=subprocess.STDOUT, shell=True, env=environ)
#except subprocess.CalledProcessError:
#    print jobnotsent()
#    quit()

print succeeded(val)