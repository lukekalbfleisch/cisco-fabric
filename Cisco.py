#!/usr/bin/env python
"""
Simple API for connecting to Cisco devices and running generic commands safely
Depends on Fabric
"""
from fabric.api import run, env, roles, task, hide, open_shell, runs_once
from fabric.colors import red, cyan, yellow
from fabric.contrib.console import confirm
from getpass import getpass

# Set up some variables to be used throught the run:
env.user = "luke"  # This is the user we'll run as
# Lets get the password via manual entry instead of displaying it in
# plain text in mercurial, eh?
#env.password = getpass(yellow("Enter password for `%s` to continue: " % 
#        env.user, bold=True))
# We define a role here, and add entries to it:
env.roledefs = {
    'routers': ['192.168.110.1', '192.168.51.1', '192.168.51.2']
}
# We need to disable host_keys on the machine we're running on, or 
# fabric/paramiko will try to use them to authenticate instead of
# our password. Slightly frustrating, but this is how we fix:
env.no_keys = True


def updateRoles(roles):
    """
    Updates our env.roledefs dictionary with a new dictionary
    Useful for adding targets on the fly. Takes and requries a dict.
    """
    if isinstance(roles, dict):
        if env.roledefs:
            try:
                env.update(roles)
            except Exception as e:
                print e
    else:
        print "Please provide updateRoles with a dictionary object!"
        return


@task(alias="en")
def enable():
    """
    Enters enabled mode. It's best to run this at the start of every connection
    to ensure we are performing our commands correctly.
    """
    try:
        run("enable", shell=False)
    except Exception as e:
        print e


@task(alias="term")
@runs_once
def termLen():
    """
    Sets our terminal length to 0, so that the entire output of our commands
    is displayed, without needing to send a key to display more.
    """
    run("terminal length 0", shell=False)


@task(alias="conf")
def config():
    """
    Enters global configuration mode. We'll ask the user if they want to
    manually enter commands from here out. If so, we'll open a shell for
    them, otherwise we'll continue on and wait for commands.
    """
    confirmation = "Entering configuration mode, "
    confirmation += "would you like to procede with manual entry?"
    if confirm(cyan(confirmation)):
        try:
            run("configure terminal", shell=False)
            print(cyan("Opening a shell for you, you may now enter commands:"))
            open_shell()
        except Exception as e:
            print e
    else:
        try:
            cyan("Entering configuration mode for automatic command entry...")
            run("configure terminal", shell=False)
        except Exception as e:
            print e


@task
def showVer():
    """
    Get and return the current version and hardware information
    """
    # We want to hide these to supress a million lines
    # of output every time we run a command:
    with hide('status', 'running', 'stdout'):
        version = run("show version", shell=False)
    return version


@task
def showMac():
    """
    Get and return the mac address table
    """
    with hide('status', 'running', 'stdout'):
        mac_table = run("show mac-address-table", shell=False)
    return mac_table


@task(alias="srun")
def showRun():
    """
    Get and return the running configuration
    """
    with hide('status', 'running', 'stdout'):
        running_config = run("show running-config", shell=False)
    return running_config


@task
def showStart():
    """
    Get and return the startup configuration
    """
    with hide('status', 'running', 'stdout'):
        start_config = run("show startup-config", shell=False)
    return start_config


@task
def showRoute():
    """
    Get and return the routing table
    """
    with hide('status', 'running', 'stdout'):
        routes = run("show ip route", shell=False)
    return routes


@task(alias="rel")
def reload10():
    """
    This command tells the router to restart in 10 minutes. As this
    is a dangerous command, we'll make sure to have a big scary prompt
    and require confirmation.
    """
    confirm_msg = "\n\t\tThis will restart this device in 10 minutes!"
    confirm_msg += "\n\t\tAre you sure you want to do this?"
    if confirm(red(confirm_msg, bold=True), default=False):
        run("reload in 10", shell=False)
        print(red("reloading in 10!", bold=True))
    else:
        print("Aborting.")


@task
def cancelReload():
    """
    This will cancel the 'reload in 10' command from reload10()
    """
    run("reload cancel", shell=False)


@task(alias="wr")
def write():
    """
    This will save the current running configuration as the startup 
    configuration.
    """
    run("write", shell=False)


## Sample tasks ##


@roles("routers")  # Define a role that this task applies to
@task  #  Make sure it's a task we can execute from the CLI, too
def getMac():
    """
    Displays the mac address table for a device
    """
    try:
        termLen()
        macs = showMac()
        print macs
    except Exception as e:
        print(cyan(e, bold=True))


@roles("routers")
@task
def getRun():
    """
    Displays the running-config for a device
    """
    try:
        termLen()
        config = showRun()
        print config
    except Exception as e:
        print(cyan(e, bold=True))


@roles("routers")
@task
def getVer():
    """
    Displays the current version and hardware for a device
    """ 
    try:
        termLen()
        a = showVer()
        print a
    except Exception as e:
        print(cyan(e, bold=True))


@roles("routers")
@task
def main():
    """
    Simply showing we can chain commands together
    """
    try:
        enable()
        #termLen()
        getMac()
        getVer()
    except Exception as e:
        print(yellow("[ERROR]" + e))


#if __name__ == '__main__':
    #main()


