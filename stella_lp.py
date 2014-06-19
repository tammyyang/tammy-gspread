#!/usr/bin/env python
#
# ./lp-set-milestone -p $PROJECT -m $MILESTONE
#

import sys
import os
import logging
from ConfigParser import SafeConfigParser
from launchpadlib.launchpad import Launchpad
from launchpadlib.launchpad import Credentials
from launchpadlib.launchpad import AccessToken

LP_VALIDATE_BUGTASK_STATUS = {
    'FIXED' : ("Fix Committed",
                    "Fix Released" ),
    'CLOSED': ("Fix Committed",
                    "Fix Released",
                    "Invalid",
                    "Won't Fix"),
    'OPEN': ("New",
                    "Incomplete (with response)",
                    "Incomplete (without response)",
                    "Incomplete",
                    "Confirmed",
                    "Triaged",
                    "In Progress" ),
    'ALL': ("New",
                    "Incomplete (with response)",
                    "Incomplete (without response)",
                    "Incomplete",
                    "Invalid",
                    "Won't Fix",
                    "Confirmed",
                    "Triaged",
                    "In Progress",
                    "Fix Committed",
                    "Fix Released" ),
}

LP_VALIDATE_BUGTASK_IMPORTANCE=("Critical",
                    "High",
                    "Medium",
                    "Low",
                    "Undecided",
                    "Wishlist" )

CONFIG_PATH=os.path.join(os.environ["HOME"], ".pes/launchpad")

class GetLaunchpadObject: 
    def __init__(self, **kwargs):
        self.input_parameters = {'staging': False,
                                 'project_name': None,
                                 'saved_credential': False}
        for key in [key for key in kwargs.keys() if kwargs[key] != None]:
            self.input_parameters[key] = kwargs[key]
        self.lp = self._login_lp(staging=self.input_parameters['staging'], saved_credential=self.input_parameters['saved_credential'])
        self.project_name = self.input_parameters['project_name'].lower()
        self.project = self.lp.projects[self.project_name]
        self.target_tasks = None
        self.base_link = "https://api.launchpad.net/1.0/"
        if self.input_parameters['staging']:
            self.base_link.replace("apt","api.staging").replace("1.0", "devel")
    def _login_lp(self, staging=False, saved_credential=False):
        cachedir = os.path.join(os.environ["HOME"], ".launchpadlib/cache")
        if saved_credential and os.path.exists(CONFIG_PATH):
            if staging:
                fatal(_("Cannot use saved credential on staging server."));    
            else:
                staging_level = "production"
                parser = SafeConfigParser()
                parser.read(CONFIG_PATH)
                credentials = Credentials(parser.get('credential', 'consumer'))
                content = ''.join(['oauth_token=', parser.get('credential', 'token'), '&oauth_token_secret=', parser.get('credential', 'secret'), '&lp.context=', parser.get('credential', 'context')])
                credentials.access_token = AccessToken.from_string(content)
                lp = Launchpad(credentials, None, None, service_root="production")
        else:
            if staging:
                staging_level = "staging"
            else:
                staging_level = "production"
            lp = Launchpad.login_with(sys.argv[0], staging_level, cachedir , version="devel")
        logging.info("Use {0} server".format(staging_level))
        if not lp:
            fatal(_("failed to connect to launchpad"));
        return lp
    
    def CopyBug(self, bug):
        newbug = self.CreateBug(title=bug.title, description=bug.description)
        bugtasks = [b for b in bug.bug_tasks]
        bug_targets = self.GetSeries(input_list=[getattr(bt, "bug_target_name").split("/")[-1] for bt in bugtasks])
        trunk_task = bugtasks[0]
        self.SetBug(newbug, tags=bug.tags, series=bug_targets)
        return newbug, trunk_task.assignee.name, trunk_task.status, trunk_task.importance

    def CreateBug(self, **kwargs):
        parameter_dic = {'title': None, 'description': None}
        for key in parameter_dic.keys():
            parameter_dic[key] = kwargs[key]
        return self.lp.bugs.createBug(
            title = parameter_dic['title'],
            description = parameter_dic['description'],
            target = self.project)

    def SetBug(self, bug, **kwargs):
        for key in [key for key in kwargs.keys() if kwargs[key] != None]:
            value = kwargs[key]
            if key == "tags":
                oldtags = bug.tags
                bug.tags = oldtags + value
            elif key == "title":
                bug.title = value
            elif key == "comment":
                bug.newMessage(content=value)
            elif key == "des":
                bug.description = value
            elif key == "series":
                bug_targets = [getattr(bt, "bug_target_name").split("/")[-1] for bt in bug.bug_tasks]
                for series in [series for series in value if (series != None and series.name not in bug_targets)]:
                    bug.addTask(target=series)
        logging.debug("SetBug: {0} processed.".format(bug.web_link))
        bug.lp_save()

    def check_empty(self, **kwargs):
        for key, value in kwargs.iteritems():
            if value == None or len(value) == 0:
                logging.error("%s is empty, please check." %key)
                raise KeyError

    def SetBugTasks(self, _tasks=None, **kwargs):
        target_tasks = self.target_tasks if _tasks == None else _tasks
        self.check_empty(target_task_list=target_tasks)
        for bugtask in target_tasks:
            trunk_task_list = [b for b in bugtask.bug.bug_tasks if b.bug_target_name == self.project_name]
            trunk_task = trunk_task_list[0] if len(trunk_task_list) >0 else None
            for key in [key for key in kwargs.keys() if kwargs[key] != None]:
                value = kwargs[key]
                if key == "status":
                    bugtask.status = value
                    bchange_trunk = True
                    if value in LP_VALIDATE_BUGTASK_CLOSEDSTATUS:
                        othertasks = filter(lambda bt: getattr(bt, "bug_target_name").find('hwe') == -1, bugtask.bug.bug_tasks)
                        other_open_tasks = [othertask for othertask in othertasks \
                                            if (othertask.bug_target_name != self.project_name \
                                            and othertask.bug_target_name != bugtask.bug_target_name)
                                            and othertask.status in LP_VALIDATE_BUGTASK_OPENSTATUS]
                        if len(other_open_tasks) > 0 or 'stella-workaround' in bugtask.bug.tags:
                            bchange_trunk = False
                    if bchange_trunk and trunk_task != None:
                        trunk_task.status = value
                elif key == "importance":
                    bugtask.importance = value
                    if trunk_task != None:
                        trunk_task.importance = value
                elif key == "assignee":
                    assignee = self.GetAssigneeLink(value)
                    bugtask.assignee = assignee
                    if trunk_task != None:
                        trunk_task.assignee = assignee
                elif key == "milestone" and bugtask.bug_target_name != self.project_name:
                    bugtask.milestone_link = value
            logging.debug("SetBugTask: {0} processed.".format(bugtask.web_link))
            bugtask.lp_save()
            if trunk_task != None:
                logging.debug("SetBugTask: {0} processed.".format(trunk_task.web_link))
                trunk_task.lp_save()

    def GetAssigneeLink(self, assignee):
        return "".join([self.base_link, "~", assignee]) if assignee != "" else None

    def DefineBugTasks(self, **kwargs):
        ''' tags: search for tasks which contain the tags defined
            keytag: search for tasks ONLY contain the tags which match this keyword'''
        bt_args = {'status': LP_VALIDATE_BUGTASK_STATUS['OPEN']}
        filter_dic = {'bug': None, 'keytag': None, 'verified': None, 'tags': None, 'series': None, 'bu': None, 'filtertrunk': True}
        target = self.project
        for key, value in kwargs.iteritems():
            if key == 'milestone':
                bt_args[key] = self.GetMilestone(value) 
            elif key == 'assignee':
                target = self.lp.people[value]
                bt_args['assignee'] = self.GetAssigneeLink(value)
            elif key == 'status':
                if value in LP_VALIDATE_BUGTASK_STATUS.keys():
                    bt_args[key] = LP_VALIDATE_BUGTASK_STATUS[value]
                else:
                    bt_args[key] = [value]
            elif key == 'series':
                target = self.GetSeries(value)
            elif key in filter_dic.keys():
                filter_dic[key] = value

        if filter_dic['bug'] != None:
            self.target_tasks = [b for b in filter_dic['bug'].bug_tasks]
            logging.debug("Searching bugtasks by bug %s" %filter_dic['bug'].id)

        else:
            self.target_tasks = [b for b in target.searchTasks(**bt_args)]

        #Filter bugtasks
        self.target_tasks = filter(lambda bt: getattr(bt, "bug_target_name").find('hwe') == -1, self.target_tasks)
        if filter_dic['filtertrunk']:
            self.target_tasks = filter(lambda bt: getattr(bt, "bug_target_name") != self.project_name, self.target_tasks)
        if filter_dic['bu'] != None:
            self.target_tasks = filter(lambda bt: getattr(bt, "bug_target_name").find(filter_dic['bu']) != -1, self.target_tasks)
        _removed_tasks = []
        if filter_dic['series'] != None:
            filter_target_names = [getattr(series, "name") for series in [target]]
            self.target_tasks = filter(lambda bt: getattr(bt, "bug_target_name").split("/")[-1] in filter_target_names, self.target_tasks)
        for b in self.target_tasks:
            if filter_dic['tags'] != None and len([[bugtag for bugtag in b.bug.tags if bugtag.find(filtertag) != -1] for filtertag in filter_dic['tags']][0]) == 0:
                _removed_tasks.append(b)
            if filter_dic['verified'] != None and len([bugtag for bugtag in b.bug.tags if bugtag in filter_dic['verified']]) == 0:
                _removed_tasks.append(b)
            if filter_dic['keytag'] != None and len([bugtag for bugtag in b.bug.tags if bugtag.find(filter_dic['keytag']) == -1]) > 0:
                _removed_tasks.append(b)
        self.target_tasks = filter(lambda bt: bt not in _removed_tasks, self.target_tasks)

    def GetTargetTasks(self):
        return self.target_tasks
    def GetBaseLink(self):
        return self.base_link
    def GetBugs(self, input_bugid_string):
        output_bug_list = []
        if input_bugid_string == None:
            logging.error("Please specify a bug id.")
            raise KeyError
        bugids = input_bugid_string.strip().split(",")
        for bugid in bugids:
            output_bug_list.append(self.lp.bugs[bugid])
        return output_bug_list
    def GetMilestone(self, milestone_name):
        return self.project.getMilestone(name=milestone_name)

    def GetMultipleMilestone(self, input_milestone_string):
        milestone_name_list = input_milestone_string.strip().split(",")
        output_milestone_list = []
        for milestone_name in milestone_name_list:
            output_milestone_list.append(self.GetMilestone(milestone_name))
        if len(output_milestone_list) == 0:
            logging.error("project milestone %s cannot be found." %milestone_name)
            raise KeyError
        else:
            logging.debug("project milestones %s found." %input_milestone_string)
        return output_milestone_list

    def GetSeries(self, series_name):
        return self.project.getSeries(name=series_name)

    def GetMultipleSeries(self, input_string=None, input_list=None):
        if input_string != None:
            series_name_list = convert_option_to_list(input_string)
        elif input_list != None:
            series_name_list = input_list
        output_series_list = []
        for series_name in series_name_list:
            output_series_list.append(self.GetSeries(series_name))
        return output_series_list

    def GetProjectName(self):
        return self.project_name

    def GetLP(self):
        return self.lp

    def GetProject(self):
        return self.project

    def GetLastCommentOrLink(self, bug):
        message_index = bug.message_count-1
        last_comment = self.GetComment(bug, message_index=message_index)
        if len(last_comment) >= 200:
            return ''.join('http://launchpad.net/bugs/',str(bug.id),'/comments/', str(message_index))
        return last_comment

    def GetComment(self, bug, message_index=-1):
        if message_index < 0:
            message_index = bug.message_count-1
        return bug.messages[message_index].content

    def FindSeriesNameFromMilestone(self, input_milestone=None):
        try:
            return input_milestone.series_target_link.split("/")[-1]
        except Exception,e:
            logging.error("Cannot find the associated series of %s milestone" %input_milestone.name)


