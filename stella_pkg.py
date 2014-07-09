import argparse
import os
import sys
import re
import subprocess
import ConfigParser
import ucltip
import debian.deb822

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

    def check_number(self, num):
        pattern = re.compile("[0-9]")
        return pattern.match(num)


class StellaBzr:
    def __init__(self, local_repo_name, remote_repo_name=None, 
                 series='trusty', ask=False, remote_prefix=None):
        ucltip.regcmds('bzr')
        self.series = series
        self.local_repo = local_repo_name
        self.remote_repo = local_repo_name if remote_repo_name is None else remote_repo_name
        self.remote_prefix = remote_prefix
        self.ask = ask

    def set_remote_repo(self, repo=None, remote_prefix=None):
        self.remote_prefix = self.remote_prefix if remote_prefix is None else remote_prefix
        self.remote_repo = self.remote_repo if repo is None else repo

    def set_local_repo(self, repo):
        self.local_repo = repo

    def valid_storage(self, path):
        return os.path.isdir(path)

    def valid_branch(self, remote_path):
        cmd = "bzr branches %s" %remote_path
        sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = sp.communicate()
        if out:
            return True
        return False

    def pull_repo(self):
        local = self.find_local()
        if self.valid_storage(local):
            print "Updating repo for %s. " %local
            bzr.pull(cwd=local)
        else:
            remote = self.find_remote()
            print "Grabing repo from %s to %s. " %(remote, local)
            bzr.branch(remote, local)

    def push_repo(self, remote=None, msg=''):
        local = self.find_local()
        print local
        if not self.valid_storage(local):
            print 'Invalid local repository'
            raise
        if self.ask and raw_input("Push local source %s to remote? [y/N]" %local) not in ['y', 'Y']:
            return
        msg = "Update {0}.".format(msg)
        try:
            bzr.add(cwd=local)
            bzr.commit(cwd=local, m=msg)
            print "Committed "
            if remote == 'parent':
                remote = ':parent'
            elif remote is None:
                remote = self.find_remote(repo_name=self.local_repo)
            print "Start pushing to %s" %remote
            bzr.push(remote, cwd=local)
            print "Done!"
        except Exception as e:
            print e
            sys.exit()

    def find_local(self):
        return os.path.join(os.getcwd(), self.local_repo)

    def find_remote(self, repo_name=None):
        repo_name = self.remote_repo if repo_name is None else repo_name
        if self.remote_prefix is None:
            prefix = "lp:~oem-solutions-group"
            if self.series == 'precise':
                project = 'stella-base'
            elif self.series == 'trusty':
                project = 'stella-trusty'
            return "{0}/{1}/{2}".format(prefix, project, repo_name)
        else:
            return "{0}/{1}".format(self.remote_prefix, repo_name)

class Stelladput:
    def __init__(self, local_repo='', series='trusty', ask=False):
        self.local_repo = local_repo
        self.series = series
        self.ask = ask
        self.common = StellaCommon()

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
        while(self.common.check_number(version[-last_num_ix])):
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
        if len(fixed_bug) > 0:
            msg += ' (LP: #%s)' %fixed_bug
        cmd = "dch -b --distribution=%s --newversion=%s --package=%s '%s'" \
            %(self.series, version, package, msg)
        self.execute_cmd(cmd)

    def execute_cmd(self, cmd):
        if self.ask and raw_input("Execute %s? [y/N]" %cmd) not in ['y', 'Y']:
            return
        try:
            os.chdir(self.local_repo)
            subprocess.call(cmd, shell=True)
            os.chdir(os.getcwd())
        except Exception as e:
            print e
            sys.exit()

    def dput(self, package, version, codename=""):
        PPA = "ppa:oem-archive/stella"
        if len(codename) > 0:
            PPA = ''.join([PPA, "-", codename]) 
        cmd = "dput -f %s ../%s_%s_source.changes" %(PPA, package, version)
        self.execute_cmd(cmd)

    def build(self):
        cmd = "dpkg-buildpackage -rfakeroot -S"
        self.execute_cmd(cmd)

    def do(self, package=None, version=None, codename="", fixed_bug="", msg=""):
        if not os.path.isdir(self.local_repo):
            print "Local repo %s does not exist!" %self.local_repo
            sys.exit()
        version = self.gen_new_version() if version is None else version
        package = self.find_package_name() if package is None else package
        self.dch(version, package, fixed_bug=fixed_bug, msg=msg)
        self.build()
        self.dput(package, version, codename=codename)

class PrepareNewPj:
    def __init__(self, pj_name, series='trusty', old_pj_name='daan'):
        self.pj_name = pj_name
        self.series = series
        self.old_pj_name = old_pj_name
        self.common = StellaCommon()

    def define_bzr_repo(self, repo, bzr):
        local_repo_name = repo.replace('CODENAME', self.pj_name)
        bzr.set_local_repo(local_repo_name)
        remote_branch = bzr.find_remote(repo_name=local_repo_name)
        if bzr.valid_branch(remote_branch):
            bzr.set_remote_repo(repo=local_repo_name)
        else:
            bzr.set_remote_repo(repo=repo.replace('CODENAME', self.old_pj_name))
        return bzr.find_local()

    def init_bugsy_config(self, codename, series):
        repo = 'stella-CODENAME-%s-amd64-osp2' %self.series
        bzr = StellaBzr('', series=series, ask=True,
                        remote_prefix='lp:~oem-solutions-engineers/bugsy-config') #set ask=False after it is stable
        local = self.define_bzr_repo(repo, bzr)
        bzr.pull_repo()
        self.common.mass_file_replacement(local, self.old_pj_name, self.pj_name,
                                          directory='chroot_sources')
        msg = 'Initialization for %s project.' %self.pj_name
        bzr.push_repo(msg=msg)

    def init_new_repos(self, series=None):
        series = self.series if series is None else series
        repos = ['volatile-task-CODENAME', 'stella-ug-CODENAME',
                 'oem-video-fglrx-CODENAME', 'stella-CODENAME-config']
        bzr = StellaBzr('', series=series, ask=True) #set ask=False after it is stable
        dput = Stelladput(series=series, ask=True) #set ask=False after it is stable
        for repo in repos: 
            local = self.define_bzr_repo(repo, bzr)
            bzr.pull_repo()
            if repo.startswith('volatile-task'):
                self.common.mass_file_replacement(local, self.old_pj_name, self.pj_name)

            else:
                self.common.mass_file_replacement(local, self.old_pj_name,
                                                  self.pj_name, directory='')
            dput.set_local_repo(local)
            msg = 'Initialization for %s project.' %self.pj_name
            version = dput.gen_new_version().replace(self.old_pj_name, self.pj_name)
            dput.do(codename=self.pj_name, fixed_bug="", msg=msg, version=version)

            bzr.push_repo(msg=msg)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--project', default=None,
                        help="Codename of the new project to create.")
    parser.add_argument('-s','--series', default='precise',
                        help="Ubuntu series (Default: precise)")
    parser.add_argument('-old','--oldpj', default='pinglin',
                        help="Codename of the old project to copy source from. (Default: pinglin)")
    args = parser.parse_args()

    if args.project is None:
        project = raw_input("Input codename of the new project to create.")
    else:
        project = args.project

    newpj = PrepareNewPj(project, series=args.series, old_pj_name=args.oldpj)
    newpj.init_new_repos()
    newpj.init_bugsy_config(project, args.series)
    
if __name__ == '__main__':
    main()

