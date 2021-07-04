#!/bin/python

'''
Written by: Phantom Raspberry Blower (The PRB)
Date: 01-04-2021
Description: Script for updating software from github. Tested on Raspberry Pi.
'''

import sh
from sh import git
import time
import os, sys
import logging

aggregated = ""
WORK_DIR = '/home/pi/'


def CheckForUpdate(workingDir=WORK_DIR):
    logging.info("Fetching most recent code from source..." + workingDir)
    # Fetch most up to date version of code.
    p = git("--git-dir=" + workingDir + ".git/",
            "--work-tree=" + workingDir, "fetch", "origin", "main",
             _out=ProcessFetch, _out_bufsize=0, _tty_in=True)
    logging.info("Fetch complete.")
    time.sleep(2)
    logging.info("Checking status for " + workingDir + "...")
    statusCheck = git("--git-dir=" + workingDir + ".git/",
                      "--work-tree=" + workingDir, "status")
    if "Your branch is up to date" in statusCheck:
        logging.info("Status check passes.")
        logging.info("Code up to date.")
        return False
    else:
        logging.info("Code update available.")
        return True


def ProcessFetch(char, stdin):
    global aggregated
    sys.stdout.flush()
    aggregated += char
    if aggregated.endswith("Password for 'https://PhantomRaspberryBlower" /
                           "/repository.prb-avss@github.com':"):
        print(mainLogger, "Entering password...", True)
        stdin.put("yourpassword\n")

if __name__ == "__main__":
    if CheckForUpdate(WORK_DIR):
        resetCheck = git("--git-dir=" + WORK_DIR + ".git/",
                         "--work-tree=" + WORK_DIR, "reset", "--hard",
                         "origin/main")
