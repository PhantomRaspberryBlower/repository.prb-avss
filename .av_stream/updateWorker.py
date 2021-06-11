import sh
from sh import git
import time
import os, sys

aggregated = ""


def CheckForUpdate(workingDir):
    print("Fetching most recent code from source..." + workingDir)
    # Fetch most up to date version of code.
    p = git("--git-dir=" + workingDir + ".git/", "--work-tree=" + workingDir,
            "fetch", "origin", "main", _out=ProcessFetch, _out_bufsize=0,
            _tty_in=True)
    print("Fetch complete.")
    time.sleep(2)
    print("Checking status for " + workingDir + "...")
    statusCheck = git("--git-dir=" + workingDir + ".git/",
                      "--work-tree=" + workingDir, "status")
    if "Your branch is up to date" in statusCheck:
        print("Status check passes.")
        print("Code up to date.")
        return False
    else:
        print("Code update available.")
        return True


def ProcessFetch(char, stdin):
    global aggregated
    sys.stdout.flush()
    aggregated += char
    if aggregated.endswith("Password for 'https://PhantomRaspberryBlower' \
                           '/repository.prb-avss@github.com':"):
        print(mainLogger, "Entering password...", True)
        stdin.put("yourpassword\n")

if __name__ == "__main__":
#    checkTimeSec = 60
#    gitDir = "/home/pi/"
#    while True:
#        print("*********** Checking for code update **************")
#        if CheckForUpdate(gitDir):
#            print("Resetting code...")
#            resetCheck = git("--git-dir=" + gitDir + ".git/",
#                              "--work-tree=" + gitDir, "reset", "--hard",
#                              "origin/main")
#            print(str(resetCheck))
#        print("Check complete. Waiting for " + str(checkTimeSec) + 
#               "seconds until next check...", True)
#        time.sleep(checkTimeSec)
    gitDir = "/home/pi/"
    if CheckForUpdate(gitDir):
        resetCheck = git("--git-dir=" + gitDir + ".git/",
                         "--work-tree=" + gitDir, "reset", "--hard",
                         "origin/main")
