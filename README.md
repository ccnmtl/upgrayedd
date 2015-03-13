# Upgrayedd

Upgrade all the apps.

## Background

I help maintain a lot of django applications (30+). They are all quite
standardized, with the same directory layout, same basic `Makefile`, and
same `requirements.txt`.

If a new Django security release or other library version comes out
and it's time to upgrade, that means I need to go into each of those
projects, and basically do:

* check the requirements.txt to see if the library to be upgraded
  is used in this project and hasn't already been upgraded.
* make a new git branch for the upgrade
* edit `requirements.txt` to update it
* run `make` to rebuild the virtualenv and run the unit tests to check
  that it didn't break anything
* git commit with an appropriate message
* git push that branch up to github
* use hub to make a pull request for the branch (then one of my
  coworkers will be notified and can review and merge)
* switch the checked out repo back to the master branch

It takes a while to do that manually for that many projects.

After doing it manually a few times (making liberal use of `C-r` and
the up-arrow in the shell to rerun the same commands), I did what any
lazy programmer would do and wrote a small shell script. Eg:

https://gist.github.com/thraxil/cdf86e6efee0fa10afc3

Then, each time I wanted to upgrade something, I would copy that shell
script and tweak it. That certainly simplified the process.

Then the bottleneck became making those little upgrade scripts. I've
been on a kick lately to get all of our projects using the same
versions of as many dependencies as possible, so even that was
becoming a chore.

This program is my latest version, to automate the automation.

## Usage

    $ ./upgrayedd.py --repos=repos.txt \
      --base=/home/anders/code/python \
      --branch=nose-1.3.4 \
      --match='nose==1.3.0' \
      --replace='nose==1.3.4' \
      --message=':arrow_up: nose 1.3.4' \
      --hub=~/bin/hub

That will look at the `repos.txt` file which should be a list of all
of your repos, one per line. It expects them to all be checked out in
the directory specified by `--base`. It will go through them in turn, 
checking for the `match` pattern in `requirements.txt`. If it finds
it, it makes the new branch specified, does the search/replace,
runs `make`, commits, pushes the branch, makes a pull request,
then resets the checkout to master. If any stage fails, it logs
it and moves on the next repository. At the end of it all, it
prints out a report summarizing which repositories it skipped (no
match found in requirements.txt), which ones failed (and which step they
failed on) so you can investigate, and which ones were successfully
upgraded.

There's also a simple, "update world" mode that just makes sure all
checked out repos are up to date:

    $ ./upgrayedd.py --repos=repos.txt \
      --base=/home/anders/code/python \
      --uworld=1

