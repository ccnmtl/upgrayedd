#!/usr/bin/env python

import subprocess
import argparse
import os


class Upgrader(object):
    def __init__(self, base, repo, branch, match, replace, message):
        self.base = base
        self.repo = repo
        self.branch = branch
        self.match = match
        self.replace = replace
        self.message = message
        self.status = "running"
        self.log = ""

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

    def upgrade(self):
        print("====== %s =======" % self.repo)
        print("cd %s" % self.full_repo_path())
        os.chdir(self.full_repo_path())
        ret = subprocess.call(["git", "checkout", "master"])
        if ret:
            self.fail("failed on git checkout")
            return
        ret = subprocess.call(["git", "pull"])
        if ret:
            self.fail("failed on git pull")
            return
        ret = subprocess.call(["grep", self.match, self.requirements_path()])
        if ret:
            self.skip()
            print("##### skipping ######")
            return
        ret = subprocess.call(["git", "checkout", "-b", self.branch])
        if ret:
            self.fail("failed to create new branch")
            return
        ret = subprocess.call(
            ["perl", "-pi", "-e", self.replace_pattern(),
             self.requirements_path()])
        if ret:
            self.fail("search/replace failed")
            return
        ret = subprocess.call(["make"])
        if ret:
            self.fail("make failed")
            return
        ret = subprocess.call(
            ["git", "commit", "-a", "-m", self.message])
        if ret:
            self.fail("commit failed")
            return
        ret = subprocess.call(
            ["git", "push", "origin", self.branch])
        if ret:
            self.fail("git push failed")
            return
        ret = subprocess.call(
            ["/home/anders/bin/hub",
             "pull-request", "-m", self.message])
        if ret:
            self.fail("pull-request failed")
            return
        ret = subprocess.call(["git", "checkout", "master"])
        if ret:
            self.fail("couldn't reset to master")
            return
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


def main(base, repos, branch, match, replace, message):
    f = open(repos)
    failed = []
    skipped = []
    succeeded = []
    for line in f:
        r = line.strip()
        u = Upgrader(base, r, branch, match, replace, message)
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
    args = parser.parse_args()
    main(args.base, args.repos, args.branch, args.match,
         args.replace, args.message)
