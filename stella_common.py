import argparse
import os
import sys
import re
import subprocess
import ConfigParser
import ucltip
import debian.deb822
from datetime import date, timedelta

class StellaCommon:
    def __init__(self, project='stella'):
        self.project = project

    def mass_file_replacement(self, local, pat, s_after, directory='debian'):
        for dirpath, dirnames, filenames in os.walk(os.path.join(local, directory)):
            for fname in filenames:
                if fname == 'changelog':
                    continue
                fullname = os.path.join(dirpath, fname)
                if os.path.isfile(fullname):
                    self.file_replace(fullname, pat, s_after)

    def file_replace(self, fname, pat, s_after):
        with open(fname) as f:
            out_fname = fname + ".tmp"
            out = open(out_fname, "w")
            for line in f:
                out.write(re.sub(pat, s_after, line))
            out.close()
            os.rename(out_fname, fname)

    def mass_file_rename(self, local, old_name_kw, new_name_kw, directory=''):
        for dirpath, dirnames, filenames in os.walk(os.path.join(local, directory)):
            for fname in filenames:
                if old_name_kw in fname:
                    old_path = os.path.join(dirpath, fname)
                    self.file_rename(old_path, old_name_kw, new_name_kw)

    def file_rename(self, path, pat, s_after):
        new_path = path.replace(pat, s_after)
        os.rename(path, new_path)

    def valid_number(self, num):
        pattern = re.compile("[0-9]")
        return pattern.match(num)

    def validate_packagename(self, package_name):
        pattern = re.compile("[0-9a-zA-Z\-]*")
        if pattern.match(package_name):
            return True
        else:
            return False

    def validate_lp_bug_num(self, num):
        pattern = re.compile("[0-9]*[0-9]")
        if pattern.match(num):
            return True
        else:
            return False

    def find_monday(self):
        today = date.today()
        monday = today + timedelta(days=-today.weekday(), weeks=0)
        return '-'.join([str(monday.year), str(monday.month), str(monday.day)])

    def deltaDate(self, d1, d2):
        d1 = d1.replace(tzinfo=None)
        d2 = d2.replace(tzinfo=None)
        if d1 is None or d2 is None:
            return np.nan
        return (d2 - d1).days

    def strify(self, result):
        try:
            result = str(result)
        except:
            result = result
        return result

