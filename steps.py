import subprocess

import requests


class Step(object):
    def __init__(self, cmd, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.cmd = cmd
        self.label = label
        self.skip_fail = skip_fail

    def run(self):
        if self.upgrader.status == 'failed':
            return
        if self.upgrader.status == 'skipped':
            return
        ret = subprocess.call(self.cmd)
        if ret:
            if self.skip_fail == 'fail':
                self.upgrader.fail(self.label)
            else:
                self.upgrader.skip()


class CommitStatusStep(object):

    def __init__(self, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.label = label
        self.skip_fail = skip_fail

    def run(self):
        if self.upgrader.status == 'failed':
            return
        if self.upgrader.status == 'skipped':
            return

        url = '{}/{}/{}/commits/{}/status'.format(
            self.upgrader.git_base, self.upgrader.owner,
            self.upgrader.repo, self.upgrader.pattern)

        response = requests.get(url, headers=self.upgrader.headers)
        if (response.status_code != 200 or
                response.json()['state'] != 'success'):
            if self.skip_fail == 'fail':
                self.upgrader.fail(self.label)
            else:
                self.upgrader.skip()


class PullRequestStep(object):

    def __init__(self, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.label = label
        self.skip_fail = skip_fail

    def run(self):
        if self.upgrader.status == 'failed':
            return
        if self.upgrader.status == 'skipped':
            return

        url = '{}/{}/{}/pulls'.format(
            self.upgrader.git_base, self.upgrader.owner, self.upgrader.repo)

        response = requests.get(url, headers=self.upgrader.headers)
        if response.status_code == 200:
            for pr in response.json():
                if self.upgrader.pattern == pr['head']['ref']:
                    self.upgrader.number = pr['number']
                    return

        # no matching pull request
        if self.skip_fail == 'fail':
            self.upgrader.fail(self.label)
        else:
            self.upgrader.skip()


class MergeStep(object):

    def __init__(self, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.label = label
        self.skip_fail = skip_fail

    def run(self):
        if self.upgrader.status == 'failed':
            return
        if self.upgrader.status == 'skipped':
            return

        url = '{}/{}/{}/pulls/{}/merge'.format(
            self.upgrader.git_base, self.upgrader.owner,
            self.upgrader.repo, self.upgrader.number)

        response = requests.put(url, headers=self.upgrader.headers)
        if response.status_code != 200:
            # no matching pull request
            if self.skip_fail == 'fail':
                self.upgrader.fail(self.label)
            else:
                self.upgrader.skip()
