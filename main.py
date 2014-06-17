#!/usr/bin/env python
import stella_lp
import mechanize
import stella_tpl
import stella_gspread
from ConfigParser import SafeConfigParser
import logging
import subprocess
import os

KEY = '0ApMQND2fzJEVdDlYYVJBZjBKRkZVMmVzZlFncmVHcVE'
TABNAME = 'Project Overview'

passphrase_path = os.path.join(os.environ["HOME"], ".tammy")
parser = SafeConfigParser()
parser.read(passphrase_path)
email = parser.get('main', 'email')
password = parser.get('main', 'password')
sgd = stella_gspread.STELLA_GSHEET(email,password, KEY, wstitle=TABNAME)
slp = stella_lp.GetLaunchpadObject(project_name='stella')


try:
    slp.DefineBugTasks(assignee='timchen119')
    tasks = slp.GetTargetTasks()
    print tasks
    for bt in tasks:
        print bt.bug.id, bt.assignee, getattr(bt, "bug_target_name").split("/")[-1]
except:
    raise 
