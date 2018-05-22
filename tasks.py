import os

from steps import Step, CommitStatusStep, PullRequestStep, MergeStep


class Task(object):

    def full_repo_path(self):
        return os.path.join(self.base, self.repo)

    def requirements_path(self):
        return os.path.join(self.base, self.repo, 'requirements.txt')

    def package_json_path(self):
        return os.path.join(self.base, self.repo, 'package.json')

    def replace_pattern(self):
        return 's/%s/%s/' % (self.match, self.replace)

    def fail(self, msg):
        self.status = 'failed'
        self.log = msg

    def skip(self):
        self.status = 'skipped'


class CloneTask(Task):
    def __init__(self, base, repo):
        self.base = base
        self.repo = repo
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.base)

        gitref = 'git@github.com:ccnmtl/{}.git'.format(self.repo)

        steps = [Step(
            ['git', 'clone', gitref],
            'git clone {}'.format(gitref),
            self)]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class CheckoutTask(Task):
    def __init__(self, base, repo, branch):
        self.base = base
        self.repo = repo
        self.branch = branch
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())

        steps = [
            Step(['git', 'checkout', self.branch],
                 'git checkout {}'.format(self.branch),
                 self),
            Step(['git', 'reset', '--hard'], 'git reset --hard',
                 self),
            Step(['git', 'pull'], 'git pull', self),
        ]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class NewBranchTask(Task):
    def __init__(self, base, repo, branch):
        self.base = base
        self.repo = repo
        self.branch = branch
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())

        steps = [
            Step(['git', 'checkout', 'master'],
                 'git checkout master', self),
            Step(['git', 'reset', '--hard'],
                 'git reset --hard', self),
            Step(['git', 'pull'],
                 'git pull', self),
            Step(['git', 'checkout', '-b', self.branch],
                 'create new branch', self),
            ]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class MakeTask(Task):
    def __init__(self, base, repo):
        self.base = base
        self.repo = repo
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())
        steps = [Step(['make'], 'make', self)]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class StatusTask(Task):
    def __init__(self, base, repo):
        self.base = base
        self.repo = repo
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())

        steps = [
            Step(['git', 'status'],
                 'git status', self),
            ]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class CommitAndPushTask(Task):
    def __init__(self, base, repo, branch, message):
        self.base = base
        self.repo = repo
        self.branch = branch
        self.message = message
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())

        print(self.full_repo_path())

        steps = [
            Step(['git', 'checkout', self.branch],
                 'set branch', self),
            Step(['git', 'commit', '-a', '-m', self.message],
                 'git commit -a -m {}'.format(self.message), self),
            Step(['git', 'push', 'origin', self.branch],
                 'push changes', self),
            ]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class PublishTask(Task):
    def __init__(self, base, repo):
        self.base = base
        self.repo = repo
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())

        steps = [
            Step(['make', 'publish'],
                 'make publish',
                 self),
        ]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class RequirementsUpdateTask(Task):
    def __init__(self, base, repo, match, replace):
        self.base = base
        self.repo = repo
        self.match = match
        self.replace = replace
        self.status = 'running'
        self.log = ''

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())

        steps = [
            Step(['perl', '-pi', '-e', self.replace_pattern(),
                 self.requirements_path()], 'search/replace',
                 self)
        ]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'
        return


class MergeMatchingPullRequestTask(Task):

    def __init__(self, base, repo, owner, pattern, api_token):
        self.base = base
        self.repo = repo
        self.owner = owner
        self.pattern = pattern
        self.status = 'running'
        self.headers = {'Authorization': 'token %s' % api_token}
        self.log = ''
        self.git_base = 'https://api.github.com/repos'

    def make(self):
        print('====== %s =======' % self.repo)
        os.chdir(self.full_repo_path())

        steps = [
            CommitStatusStep('commit status', self),
            PullRequestStep('pull request info', self),
            MergeStep('merge the pr', self),
        ]

        for s in steps:
            s.run()
        if self.status != 'failed' and self.status != 'skipped':
            self.status = 'success'


class TaskRunner(object):
    failed = []
    skipped = []
    succeeded = []

    def run(self, task):
        task.make()
        if task.status == 'failed':
            self.failed.append((task.repo, task.log))
        elif task.status == 'skipped':
            self.skipped.append(task.repo)
        else:
            self.succeeded.append(task.repo)

    def print_report(self):
        print('===============================================')
        print('failed: %d' % len(self.failed))
        print('skipped: %d' % len(self.skipped))
        print('succeeded: %d' % len(self.succeeded))
        if len(self.skipped) > 0:
            print('SKIPPED:')
            for s in self.skipped:
                print('\t%s' % s)
        if len(self.failed) > 0:
            print('FAILED:')
            for (r, msg) in self.failed:
                print('\t%s: %s' % (r, msg))
        if len(self.succeeded) > 0:
            print('SUCCEEDED:')
            for r in self.succeeded:
                print('\t%s' % r)
        print('===============================================')
