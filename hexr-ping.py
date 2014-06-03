#!/usr/bin/env python
import stella_lp
import stella_gspread
import subprocess
import os
from ConfigParser import SafeConfigParser

KEY = '0AoG28UThR6GSdHJUbDZvaC1pallqaXlxRzBWcEpnVEE'
TABNAME = 'vNB-Stella-Puli'

passphrase_path = os.path.join(os.environ["HOME"], ".tammy")
parser = SafeConfigParser()
parser.read(passphrase_path)
email = parser.get('main', 'email')
password = parser.get('main', 'password')
sgd = stella_gspread.STELLA_GSHEET(email,password, KEY, wstitle=TABNAME)

hexr_index = sgd.find_rows_index('HEXR Link')[0]
hexr_row = sgd.row_values(row_index=hex_index)[1:]

f = open('/tmp/hexr-ping.log', 'w')
retry_list = []

def sign_off_main(sign_off_list):
    retry_list = []
    for i in range(0, len(sign_off_list)):
        if sign_off_list[i] == None:
            continue
        cmd = "casperjs /home/tammy/SOURCE/PES/stella-tools/hexr/hexr-ping.js '%s' ; exit 0" %(sign_off_list[i])
        casper_proc = subprocess.Popen(cmd, universal_newlines=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = casper_proc.stdout.read()
        if result.find("[phantom] Done 15 steps in") != 0:
            print "WARNING: %s does not complete successfully!" %sign_off_list[i]
            retry_list.append(sign_off_list[i]) 
        f.write(result)
        f.write('\n\n')
    return retry_list

while len(hexr_row) >=1:
    print hexr_row
    hexr_row = sign_off_main(hexr_row)

