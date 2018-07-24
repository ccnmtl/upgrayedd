import subprocess

import requests


class Step(object):
    def __init__(self, cmd, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.cmd = cmd
        self.label = label
        self.skip_fail = skip_fail

    def fail(self):
        if self.skip_fail == 'fail':
            self.upgrader.fail(self.label)
        else:
            self.upgrader.skip()

    def run(self):
        if self.upgrader.status == 'failed':
            return
        if self.upgrader.status == 'skipped':
            return

        ret = self.execute()

        if ret:
            if self.skip_fail == 'fail':
                self.upgrader.fail(self.label)
            else:
                self.upgrader.skip()

    def execute(self):
        return subprocess.call(self.cmd)


class CommitStatusStep(Step):

    def __init__(self, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.label = label
        self.skip_fail = skip_fail

    def execute(self):
        url = '{}/{}/{}/commits/{}/status'.format(
            self.upgrader.git_base, self.upgrader.owner,
            self.upgrader.repo, self.upgrader.pattern)

        response = requests.get(url, headers=self.upgrader.headers)
        if response.status_code != 200:
            return 1

        the_json = response.json()
        for status in the_json['statuses']:
            # ignore pyup safety warnings
            if status['context'] == 'pyup.io/safety-ci':
                continue
            if status['state'] == 'failure':
                return 1


class PullRequestStep(Step):

    def __init__(self, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.label = label
        self.skip_fail = skip_fail

    def execute(self):
        url = '{}/{}/{}/pulls'.format(
            self.upgrader.git_base, self.upgrader.owner, self.upgrader.repo)

        response = requests.get(url, headers=self.upgrader.headers)
        if response.status_code != 200:
            return 1

        for pr in response.json():
            if self.upgrader.pattern == pr['head']['ref']:
                self.upgrader.number = pr['number']
                return

        return 1


class MergeStep(Step):

    def __init__(self, label, upgrader, skip_fail='fail'):
        self.upgrader = upgrader
        self.label = label
        self.skip_fail = skip_fail

    def execute(self):
        url = '{}/{}/{}/pulls/{}/merge'.format(
            self.upgrader.git_base, self.upgrader.owner,
            self.upgrader.repo, self.upgrader.number)

        response = requests.put(url, headers=self.upgrader.headers)
        if response.status_code != 200:
            return 1
