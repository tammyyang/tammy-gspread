#!/usr/bin/python
import os
import os.path
import imp
import supybot.stella_gspread as stella_gspread
import supybot.stella_lp as stella_lp

passfile = os.path.expanduser("~/.pes/ircbot/stellapass")
stellapass = imp.load_source("stellapass",passfile)

sgd = stella_gspread.STELLA_GSHEET(stellapass.SSO_ACCOUNT, stellapass.SSO_PASSWORD, '0ApMQND2fzJEVdDlYYVJBZjBKRkZVMmVzZlFncmVHcVE', wstitle='Project Overview')
slp = stella_lp.GetLaunchpadObject(saved_credential=True, project_name='stella')
