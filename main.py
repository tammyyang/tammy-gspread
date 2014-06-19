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

def deltaDate(d1, d2):
    d1 = d1.replace(tzinfo=None)
    d2 = d2.replace(tzinfo=None)
    if d1 is None or d2 is None:
        return np.nan
    return (d2 - d1).days

def calHPS(bug):
    sgd.set_selfws_by_title('Project Overview')
    gm_col_index = sgd.find_col_index('GM Date')
    series_col_values = sgd.col_values(col_index=1)
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
        if bug_target not in series_col_values:
            continue
        gm_row_index = series_col_values.index(bug_target) + 1
        gm_date = datetime.strptime(sgd.get_cell(gm_row_index, gm_col_index), '%Y/%m/%d')
        days_to_gm = deltaDate(today, gm_date)
        tmp += 0.2 if days_to_gm <= 14 else 0
        tmp += 0.1 if days_to_gm <= 7 else 0

        hps_sub = tmp if tmp > hps_sub else hps_sub
    return hps_main + hps_sub

def find_ppa(input_query=None):
    series_list = sgd.col_values('LP Series')
    if validate_lp_bug_num(input_query):
        bug = slp.GetBugs(input_query)[0]
        slp.DefineBugTasks(bug=bug)
        tags = bug.tags
        for bt in getlp.GetTasks():
            if bt.status not in LP_VALIDATE_BUGTASK_STATUS['OPEN']:
                continue
            series =  getattr(bt, "bug_target_name").split("/")[-1]
            if series not in series_list:
                continue
            milestone = getattr(bt, "milestone")
            if milestone == None:
                gdoc_index = sgd.find_row_index(series)
            elif 'daan-140425-' in milestone:
                gdoc_index = sgd.find_row_index('daan2')
            else:
                gdoc_index = sgd.find_row_index(milestone.name.split("-")[0])

            bzr_src = source_list[gdoc_index]
            if bzr_src not in ppa_source_map.keys():
                ppa_source_map[bzr_src] = {'ppa':[],'ibs':[], 'base':''}
            if "Active" in status_list[gdoc_index] and
stella_ppa_list[gdoc_index] != 'N/A':
                ppa_source_map[bzr_src]['ppa'].append(stella_ppa_list[gdoc_index])
            elif project_ppa_list[gdoc_index] != 'N/A':
                _project_ppa = project_ppa_list[gdoc_index].split("\n")
                if 'stella-patch' in bug_tags :
                    ppa_source_map[bzr_src]['ppa'].append(_project_ppa[-1])
                else:
                    ppa_source_map[bzr_src]['ppa'].append(_project_ppa[0])
            ppa_source_map[bzr_src]['ibs'].append(ibs_list[gdoc_index])

try:
    find_ppa('1329284')
except:
    raise 
