#!/usr/bin/env python

import subprocess
import argparse
import os


class Step(object):
    def __init__(self, cmd, label, upgrader, skip_fail="fail"):
        self.upgrader = upgrader
        self.cmd = cmd
        self.label = label
        self.skip_fail = skip_fail

    def run(self):
        if self.upgrader.status == "failed":
            return
        if self.upgrader.status == "skipped":
            return
        ret = subprocess.call(self.cmd)
        if ret:
            if self.skip_fail == "fail":
                self.upgrader.fail(self.label)
            else:
                self.upgrader.skip()


class UBase(object):
    def full_repo_path(self):
        return os.path.join(self.base, self.repo)

    def requirements_path(self):
        return os.path.join(self.base, self.repo, "requirements.txt")

    def replace_pattern(self):
        return "s/%s/%s/" % (self.match, self.replace)

    def fail(self, msg):
        self.status = "failed"
        self.log = msg

    def skip(self):
        self.status = "skipped"


class Upgrader(UBase):
    def __init__(self, base, repo, branch, match, replace, message, hub):
        self.base = base
        self.repo = repo
        self.branch = branch
        self.match = match
        self.replace = replace
        self.hub = hub
        self.message = message
        self.status = "running"
        self.log = ""

    def upgrade(self):
        print("====== %s =======" % self.repo)
        os.chdir(self.full_repo_path())
        steps = [
            Step(["git", "checkout", "master"],
                 "git checkout master", self),
            Step(["git", "pull"],
                 "git pull", self),
            Step(["grep", self.match, self.requirements_path()],
                 "grep", self, skip_fail="skip"),
            Step(["git", "checkout", "-b", self.branch],
                 "create new branch", self),
            Step(["perl", "-pi", "-e", self.replace_pattern(),
                  self.requirements_path()], "search/replace",
                 self),
            Step(["make"], "make", self),
            Step(["git", "commit", "-a", "-m", self.message],
                 "commit", self),
            Step(["git", "push", "origin", self.branch],
                 "push", self),
            Step([self.hub,
                  "pull-request", "-m", self.message],
                 "pull request", self),
            Step(["git", "checkout", "master"], "reset to master",
                 self),
            ]
        for s in steps:
            s.run()
        if self.status != "failed" and self.status != "skipped":
            self.status = "success"
        return


class Updater(UBase):
    def __init__(self, base, repo):
        self.base = base
        self.repo = repo
        self.status = "running"
        self.log = ""

    def upgrade(self):
        print("====== %s =======" % self.repo)
        os.chdir(self.full_repo_path())
        steps = [
            Step(["git", "checkout", "master"],
                 "git checkout master", self),
            Step(["git", "pull"],
                 "git pull", self),
            ]
        for s in steps:
            s.run()
        if self.status != "failed" and self.status != "skipped":
            self.status = "success"
        return


def print_report(failed, skipped, succeeded):
    print("===============================================")
    print("failed: %d" % len(failed))
    print("skipped: %d" % len(skipped))
    print("succeeded: %d" % len(succeeded))
    if len(skipped) > 0:
        print("SKIPPED:")
        for s in skipped:
            print("\t%s" % s)
    if len(failed) > 0:
        print("FAILED:")
        for (r, msg) in failed:
            print("\t%s: %s" % (r, msg))
    if len(succeeded) > 0:
        print("SUCCEEDED:")
        for r in succeeded:
            print("\t%s" % r)
    print("===============================================")


def main(base, repos, branch, match, replace, message, uworld, hub):
    f = open(repos)
    failed = []
    skipped = []
    succeeded = []
    for line in f:
        r = line.strip()
        if uworld:
            u = Updater(base, r)
            u.upgrade()
        else:
            u = Upgrader(base, r, branch, match, replace, message, hub)
            u.upgrade()
        if u.status == "failed":
            failed.append((r, u.log))
        elif u.status == "skipped":
            skipped.append(r)
        else:
            succeeded.append(r)
    print_report(failed, skipped, succeeded)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='upgrade libraries')
    parser.add_argument('--base', help='base directory')
    parser.add_argument(
        '--repos', help='path to repos.txt file', default='repos.txt')
    parser.add_argument('--branch', help='git branch name')
    parser.add_argument('--match', help='regexp to match in requirements.txt')
    parser.add_argument('--replace', help='replacement')
    parser.add_argument('--message', help='commit and PR message')
    parser.add_argument('--uworld', help='just update everything')
    parser.add_argument('--hub', help='path to hub', default='/usr/local/bin/hub')
    args = parser.parse_args()
    main(args.base, args.repos, args.branch, args.match,
         args.replace, args.message, args.uworld, args.hub)
