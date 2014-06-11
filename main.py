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

def find_Series(milestone_name):
    milestone = slp.GetMilestone(milestone_name)
    return slp.FindSeriesNameFromMilestone(milestone)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
triaged_types = ['oem-odm-issue', 'triaged-bios', 'triaged-ihv']
argument = 'switch-display'
assign_to = 1
try:
    bug = slp.GetBugs('1328757')[0]
    print bug.link
    assignment_wks = sgd.get_sheet_by_title('Issue Assignment')
    print sgd.col_values(col_index=1)
    assign_row_values =  sgd.row_values(keyword=argument, _wks=assignment_wks)
    slp.DefineBugTasks(bug=bug)
    tasks = slp.GetTargetTasks()
    for bt in tasks:
        if assign_row_values[2] == 'N/A':
            bug_target = getattr(bt, "bug_target_name").split("/")[-1]
            assignee = sgd.get_cell(sgd.find_row_index(keyword=bug_target), sgd.find_col_index(keyword=assign_row_values[1]))
        else:
            assignee = assign_row_values[assign_to]
        slp.SetBugTasks(_tasks=[bt], assignee=assignee)
    if len(assign_row_values) > 3:
        slp.SetBug(bug=bug, comment=assign_row_values[3])
except:
    raise 
