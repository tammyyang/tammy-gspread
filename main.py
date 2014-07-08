#!/usr/bin/env python
import stella_lp
import mechanize
from datetime import datetime
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
MAINSTREAM_ENG_LIST = sgd.col_values(keyword='Mainstream Engineer ID')[1:]
ACTIVE_PROJECTS = ['stella'] + sgd.col_values(keyword='LP Series')[1:] + ['stella-base']


def deltaDate(d1, d2):
    d1 = d1.replace(tzinfo=None)
    d2 = d2.replace(tzinfo=None)
    if d1 is None or d2 is None:
        return np.nan
    return (d2 - d1).days

def calHPS(bug):
    sgd.set_selfws_by_title('Project Overview')
    gm_col_index = sgd.find_col_index('GM Date')
    hps_main = 0
    if 'stella-oem-highlight' in bug.tags:
        hps_main += 1.1
    if 'SIO ' in bug.title or 'OEM ' in bug.title:
        hps_main += 0.2
    slp.DefineBugTasks(bug=bug)
    hps_sub = 0
    for bt in slp.GetTargetTasks():
        if bt.status in stella_lp.LP_VALIDATE_BUGTASK_STATUS['CLOSED']:
            continue
        tmp = {'Critical':1.2, 'High':1.0, 'Medium': -0.2, 'Low': -0.3, 'Wishlist': -0.4, 'Undecided': -0.5}[bt.importance]

        today = datetime.now()
        tmp += (lambda x: 0.5 if x > 35 else (x/7)*0.1)(deltaDate(bt.date_created, today))

        bug_target = getattr(bt, "bug_target_name").split("/")[-1]
        if bug_target not in ACTIVE_PROJECTS:
            continue
        #Raise the priority of RPOS and WGBU (should be removed after mid of Jul 2014)
        if 'rpos' in bug_target or 'wgbu' in bug_target:
            tmp += 0.2
        if bug_target not in ['stella-base']:
            gm_row_index = ACTIVE_PROJECTS.index(bug_target) + 1
            gm_date = datetime.strptime(sgd.get_cell(gm_row_index, gm_col_index), '%Y/%m/%d')
            days_to_gm = deltaDate(today, gm_date)
            tmp += 0.2 if days_to_gm <= 14 else 0
            tmp += 0.1 if days_to_gm <= 7 else 0

        hps_sub = tmp if tmp > hps_sub else hps_sub

    return hps_main + hps_sub

def find_monday():
    from datetime import date, timedelta
    today = date.today()
    monday = today + timedelta(days=-today.weekday(), weeks=0)
    return '-'.join([str(monday.year), str(monday.month), str(monday.day)])

def deltaDate(d1, d2):
    d1 = d1.replace(tzinfo=None)
    d2 = d2.replace(tzinfo=None)
    if d1 is None or d2 is None:
        return np.nan
    return (d2 - d1).days

def find_release_today():
    release_wks = sgd.get_sheet_by_title(find_monday())
    col_index = sgd.find_col_index(keyword='LP Milestone', _wks=release_wks)
    release_time_list = sgd.col_values(keyword='Expect Time', _wks=release_wks)[1:]
    for i in range(0, len(release_time_list)):
        if release_time_list[i] is None:
            break
        release_date = datetime.strptime(release_time_list[i].split(' ')[0], '%Y/%m/%d')
        detla_days = deltaDate(datetime.now(), release_date)
        if  detla_days == 0:
            print 'Today: %s' %(sgd.get_cell(i+2, col_index, _wks=release_wks))
        elif detla_days > 0:
            print 'In %i days: %s' %(detla_days, 
                                     sgd.get_cell(i+2, col_index, _wks=release_wks)) 
import re
def validate_num(num):
    pattern = re.compile("[0-9]")
    if pattern.match(num):
        return True
    else:
        return False

try:
    userid='gerald-yang-tw'
    slp.DefineBugTasks(assignee=userid)
    tasks = slp.GetTargetTasks()
    printed_bug = {}
    total_hps = 0
    excluded_tag_preffix = ['stella-', 'hwe-', 'oem-', 'fae-']
    pattern = re.compile("[0-9]")
    for bt in tasks:
        platform_tags = [tag for tag in bt.bug.tags if pattern.match(tag[-1])]
        print platform_tags
        bugid = bt.bug.id
        if getattr(bt, "bug_target_name").split("/")[-1] not in ACTIVE_PROJECTS:
            continue
        if bugid in printed_bug.keys():
            continue
        print bugid, getattr(bt, "bug_target_name").split("/")[-1]
        HPS = calHPS(bt.bug)
        print HPS
        total_hps += HPS
        if HPS >= 1.0:
            printed_bug[bugid] = [HPS, bt.bug.title]
    print printed_bug

except:
    raise 
