#!/usr/bin/env python
import stella_lp
import stella_tpl
import stella_gspread
from ConfigParser import SafeConfigParser
import subprocess
import os

passphrase_path = os.path.join(os.environ["HOME"], ".tammy")
parser = SafeConfigParser()
parser.read(passphrase_path)
email = parser.get('main', 'email')
password = parser.get('main', 'password')
sgd = stella_gspread.STELLA_GSHEET(email,password,'0ApMQND2fzJEVdDlYYVJBZjBKRkZVMmVzZlFncmVHcVE',wstitle='Project Overview')
slp = stella_lp.GetLaunchpadObject(project_name='stella')

'''
hex_index = sgd.find_row_index('HEXR Link')
hex_row = sgd.row_values(row_index=hex_index)
for i in range(1, len(hex_row)):
    twofa = subprocess.Popen('python /home/tammy/.2fa/2fa.py', universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    otp = twofa.stdout.read().split("\n")[0]
    cmd = "casperjs /home/tammy/.2fa/hexr-ping.js '%s' '%s'" %(hex_row[i], otp)
    print cmd
    result = os.popen(cmd).read()
    print result
    break

series = slp.FindSeriesNameFromMilestone(milestone)
slp.DefineBugTasks(status='Fix Committed', series=series, milestone=milestone)
bug_tasks = slp.GetTargetTasks()
tags = []
rows = []
excluded_tags = ['stella-oem-highlight']
for bt in bug_tasks:
    tags.extend([tag for tag in bt.bug.tags if tag[0:7] == 'stella-' and tag not in excluded_tags])
    rows.append([bt.bug.id, bt.bug.title, "", "", bt.bug.tags])
sgd.add_rows(rows, _wks=copied_wks)
from collections import Counter
c = Counter(tags)
sgd.update('C1', c.most_common(2)[0][0], _wks=copied_wks)
sgd.update('D1', c.most_common(2)[1][0], _wks=copied_wks)
'''
