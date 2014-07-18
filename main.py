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
import debian.deb822
import bz2

KEY = '0ApMQND2fzJEVdDlYYVJBZjBKRkZVMmVzZlFncmVHcVE'
TABNAME = 'Project Overview'

passphrase_path = os.path.join(os.environ["HOME"], ".tammy")
parser = SafeConfigParser()
parser.read(passphrase_path)
cesg_username = parser.get('main', 'cesg_username')
cesg_password = parser.get('main', 'cesg_password')
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

def fetch_cnb_platform_info(wks, platform):
    ix = {'arc': sgd.find_col_index('Architecture', _wks=wks)-1,
          'sid': sgd.find_col_index('System Board ID', _wks=wks)-1,
          'gm': sgd.find_col_index('GM', _wks=wks)-1}
    pinfo = sgd.row_values(keyword=platform, _wks=wks)
    plist = []
    if pinfo[ix['sid']] is None or pinfo[ix['gm']] is None:
        return []
    for pid in pinfo[ix['sid']].split('\n'):
        plist.append([pid, platform, pinfo[ix['gm']], pinfo[ix['arc']]])
    return plist

def create_cnb_platform_info_table(key='1GXTg4t7FYeHAArVMxU1AJV_9tbiKrldSfHYIlb1QMkc'):
    id_sheet = sgd.gc.open_by_key(key)
    id_wks = sgd.get_sheet_by_index(0, _sheet=id_sheet)
    tags = sgd.col_values(keyword='Platform Tag', _wks=id_wks)
    platform_list = []
    for tag in tags:
        if tag == 'Platform Tag' or tag is None:
            continue
        platform_list += fetch_cnb_platform_info(id_wks, tag)
    with open('/tmp/platform-compatibility-list', 'w') as f:
        f.write('declare -A platformLookupTable=(\n')
        for item in platform_list:
            f.write(('    ["%s"]="%s:%s" #%s\n' \
                      %(item[0].strip().replace('0x', '').lower(), \
                        item[1], item[2].replace('/','-'), item[3])).encode('utf-8'))
        f.write(')')
    f.close()

    


try:
    create_cnb_platform_info_table()

except:
    raise 
