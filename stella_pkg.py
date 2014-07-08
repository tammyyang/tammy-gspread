import argparse
import os
import sys
import re
import ConfigParser
import ucltip
import debian.deb822

#ucltip.regcmds('bzr')

cfgfile = os.getenv('HOME') + '/.pes/stella-new-project.conf'

config = ConfigParser.RawConfigParser()

class StellaBzr:
    def __init__(self, local_repo_name, remote_repo_name=None, series='trusty'):
        ucltip.regcmds('bzr')
        self.series = series
        self.local_repo = local_repo_name
        self.remote_repo = local_repo_name if remote_repo_name is None else remote_repo_name

    def set_remote_repo(self, repo):
        self.remote_repo = repo

    def set_local_repo(self, repo):
        self.local_repo = repo

    def valid_storage(self, path):
        return os.path.isdir(path)

    def pull_repo(self):
        local = self.find_local()
        remote = self.find_remote()
        if self.valid_storage(local):
            print "Updating repo for %s. " %local
            bzr.pull(cwd=local)
        else:
            print "Grabing repo from %s to %s. " %(remote, local)
            bzr.branch(remote, local)

    def push_repo(self, remote=None, msg=''):
        local = self.find_local()
        if not self.valid_storage(local):
            print 'Invalid local repository'
            raise
        msg = "Update {0}.".format(msg)
        try:
            bzr.add(cwd=local)
            bzr.commit(cwd=local, m=msg)
            print "Committed "
            print "Starting to push.... "
            if remote == 'parent':
                remote = ':parent'
            elif remote is None:
                remote = self.find_remote()
            bzr.push(remote, cwd=local)
            print "Done!"
        except Exception as e:
            print e
            sys.exit()

    def find_local(self):
        return os.path.join(os.getcwd(), self.local_repo)

    def find_remote(self):
        prefix = "lp:~oem-solutions-group"
        if self.series == 'precise':
            project = 'stella-base'
        elif self.series == 'trusty':
            project = 'stella-trusty'
        return "{0}/{1}/{2}".format(prefix, project, self.remote_repo)

class Stelladput:
    def __init__(self, local_repo='', series='trusty'):
        self.local_repo = local_repo
        self.series = series
        self.pwd = os.getcwd()

    def set_series(self, series):
        self.series = series

    def set_local_repo(self, repo):
        self.local_repo = repo

    def find_latest_version(self):
        changelog = os.path.join(self.local_repo, 'debian/changelog')
        with open(changelog, 'r') as f:
            for line in f:
                if ''.join([self.series, ';']) in line:
                    return line.split("(")[1].split(")")[0]

    def gen_new_version(self):
        version = self.find_latest_version()
        last_num_ix = 1
        while(self.check_number(version[-last_num_ix])):
            last_num_ix += 1
        last_num_ix = last_num_ix - 1
        vnumber = int(version[-last_num_ix:]) + 1
        return ''.join([version[:-last_num_ix], str(vnumber)])

    def find_package_name(self):
        control = os.path.join(self.local_repo, 'debian/control')
        with open(control, 'r') as f:
            for line in f:
                if 'Package:' in line:
                    return line.split(':')[-1].strip()
            #while True:
                #return debian.deb822.Deb822(f)['package']

    def dch(self, version, package, fixed_bug='', msg=''):
        os.chdir(self.local_repo)
        if len(fixed_bug) > 0:
            msg += ' (LP: #%s)' %fixed_bug
        cmd = "dch -b --distribution=%s --newversion=%s --package=%s '%s'" \
            %(self.series, version, package, msg)
        self.execute_cmd(cmd)
        os.chdir(self.pwd)

    def execute_cmd(self, cmd):
        print cmd
        try:
            os.system(cmd)
        except Exception as e:
            print e
            sys.exit()

    def dput(self, package, version, codename=""):
        PPA = "ppa:oem-archive/stella"
        if len(codename) > 0:
            PPA = ''.join([PPA, "_", codename]) 
        cmd = "dput -f %s ../%s_%s_source.changes" %(PPA, package, version)
        self.execute_cmd(cmd)

    def build(self, repo=None):
        repo = self.local_repo if repo is None else repo
        os.chdir(repo)
        cmd = "dpkg-buildpackage -rfakeroot -S"
        self.execute_cmd(cmd)
        os.chdir(self.pwd)

    def do(self, package=None, version=None, codename="", fixed_bug="", msg=""):
        if not os.path.isdir(self.local_repo):
            print "Local repo %s does not exist!" %self.local_repo
            sys.exit()
        version = self.gen_new_version() if version is None else version
        package = self.find_package_name() if package is None else package
        self.dch(version, package, fixed_bug=fixed_bug, msg=msg)
        self.build()
        self.dput(package, version, codename=codename)

    def check_number(self, num):
        pattern = re.compile("[0-9]")
        return pattern.match(num)


class PrepareNewPj:
    def __init__(self, pj_name, series='trusty', old_pj_name='daan'):
        self.pj_name = pj_name
        self.series = series
        self.old_pj_name = old_pj_name
        self.bzr = StellaBzr('', series=series)
        self.dput = Stelladput(series=series)
        self.init_new_repos()

    def init_new_repos(self):
        repos = ['volatile-task-CODENAME', 'stella-ug-CODENAME', 'stella-CODENAME-config']
        for repo in repos: 
            #Prepare the source
            self.bzr.set_local_repo(repo.replace('CODENAME', self.pj_name))
            self.bzr.set_remote_repo(repo.replace('CODENAME', self.old_pj_name))
            self.bzr.pull_repo()
            local = self.bzr.find_local()
            self.mass_file_replacement(local, self.old_pj_name, self.pj_name)
            self.dput.set_local_repo(local)
            msg = 'Initialization for %s project.' %self.pj_name
            version = self.dput.gen_new_version().replace(self.old_pj_name, self.pj_name)
            self.dput.do(codename=self.pj_name, fixed_bug="", msg=msg, version=version)
            self.bzr.push_repo(msg=msg)

    def mass_file_replacement(self, local, pat, s_after):
        for dirpath, dirnames, filenames in os.walk(os.path.join(local, 'debian')):
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

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', help='project.')
    opts = parser.parse_args()
    newpj = PrepareNewPj('jian', series='precise', old_pj_name='pinglin')
    
if __name__ == '__main__':
    main()

