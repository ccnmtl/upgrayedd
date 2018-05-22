import argparse

from tasks import (
    TaskRunner, CloneTask, CheckoutTask, NewBranchTask, MakeTask,
    CommitAndPushTask, StatusTask, PublishTask, RequirementsUpdateTask,
    MergeMatchingPullRequestTask)


def main(args):
    base = args.base
    repos = args.repos

    f = open(repos)

    if args.clone:
        print('Clone')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(CloneTask(base, r))
        runner.print_report()

    if args.status:
        print('Status')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(StatusTask(base, r))
        runner.print_report()

    if args.checkout:
        print('Checkout a branch')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(CheckoutTask(base, r, args.checkout))
        runner.print_report()

    if args.new_branch:
        print('Create New Branch')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(NewBranchTask(base, r, args.new_branch))
        runner.print_report()

    if args.make:
        print('Make All')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(MakeTask(base, r))
        runner.print_report()

    if args.commit:
        print('Commit And Push')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(CommitAndPushTask(base, r, args.commit, args.message))
        runner.print_report()

    if args.publish:
        print('Publish')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(PublishTask(base, r))
        runner.print_report()

    if args.match and args.replace:
        print('Requirements Update')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(
                RequirementsUpdateTask(base, r, args.match, args.replace))
        runner.print_report()

    if args.match and args.owner:
        print('Merge pull request')
        runner = TaskRunner()
        for line in f:
            r = line.strip()
            runner.run(
                MergeMatchingPullRequestTask(
                    base, r, args.owner, args.match, args.api_token))
        runner.print_report()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='upgrade libraries')
    parser.add_argument(
        '--base', help='base directory')
    parser.add_argument(
        '--repos', help='path to repos.txt file', default='./repos.txt')

    parser.add_argument(
        '--clone', action='store_true', help='full repo clone')

    parser.add_argument(
        '--checkout', help='checkout this branch')

    parser.add_argument(
        '--new_branch', help='git branch name')

    parser.add_argument(
        '--make', action='store_true', help='make all targets')

    parser.add_argument(
        '--commit', help='git branch name to commit to')
    parser.add_argument(
        '--message', help='commit message')

    parser.add_argument(
        '--status', action='store_true', help='status')

    parser.add_argument(
        '--publish', action='store_true', help='publish')

    parser.add_argument(
        '--match', help='pattern to match')

    parser.add_argument(
        '--replace', help='pattern to replace')

    parser.add_argument(
        '--owner', help='repo owner')

    parser.add_argument(
        '--api_token', help='Github oauth token')

    args = parser.parse_args()
    main(args)
