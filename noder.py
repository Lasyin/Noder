#!/usr/bin/env python

# Bryan Collins
# Noder is a simple tool for deploying and running scripts on a remote server

import subprocess
import sys
import argparse
import os
import time
import signal
import pickle
import appdirs

APP_NAME = "noder" # used for appdirs to construct a storage directory
APP_AUTHOR = "bryan" # used for appdirs to construct a storage directory

user = 0 # global variable user keeps track of user Info class

DATA = "noder_data.pickle" #Name of data file that holds user Info class

class Info:
    def __init__(self, local_path, server_path, server_hostname, server_username, run_command):
        self._local_path = local_path
        self._server_path = server_path
        self._server_hostname = server_hostname
        self._server_username = server_username
        self._run_command = run_command

    @property
    def local_path(self):
        return self._local_path
    @local_path.setter
    def local_path(self, value):
        self._local_path=value
    @local_path.deleter
    def local_path(self):
        del self._local_path

    @property
    def server_path(self):
        return self._server_path
    @server_path.setter
    def server_path(self, value):
        self._server_path=value
    @server_path.deleter
    def server_path(self):
        del self._server_path

    @property
    def server_hostname(self):
        return self._server_hostname
    @server_hostname.setter
    def server_hostname(self, value):
        self._server_hostname=value
    @server_hostname.deleter
    def server_hostname(self):
        del self._server_hostname

    @property
    def server_username(self):
        return self._server_username
    @server_username.setter
    def server_username(self, value):
        self._server_username=value
    @server_username.deleter
    def server_username(self):
        del self._server_username

    @property
    def run_command(self):
        return self._run_command
    @run_command.setter
    def run_command(self, value):
        self._run_command=value
    @run_command.deleter
    def run_command(self):
        del self._run_command

def save_data_file(local_path, server_path, server_hostname, server_username, run_command='node app.js'):
    #Create and pickle the user Info class and save to storage dir
    global user

    user = Info(local_path, server_path, server_hostname, server_username, run_command)

    dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)

    print("open: " + os.path.join(dir, DATA))
    try:
        f = open(os.path.join(dir, DATA), 'wb')
    except IOError:
        #Errored most likely because directory does not exist
        os.makedirs(dir)
        f = open(os.path.join(dir, DATA), 'wb')

    pickle.dump(user, f)
    f.close()

def extract_data_file():
    #Extract pickled user Info class from storage dir
    global user

    dir = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    f = open(os.path.join(dir, DATA), 'rb')
    user = pickle.load(f)
    f.close()

def upload_server(local_path, server_path, server_hostname, server_username, run_command, node_modules, npm_install, rsync_del):
    cmd = "rsync -av "
    if(rsync_del == True):
        cmd += "--delete "
    if(node_modules == False):
        #Defaults to false, usually not wanted to upload node modules, much preferable to instead use npm install on server side
        cmd += "--exclude node_modules/ "
    if(not os.path.exists(local_path)):
        if(not os.path.exists(os.path.join(os.getcwd(), dir))):
            print("Error: " + local_path + " does not exist as a local path.")
            exit()
        else:
            local_path = os.path.join(os.getcwd(), dir)

    cmd += local_path + " "

    # TODO: check if server path exists to fail gracefully
    cmd += server_username + "@" + server_hostname + ":" + server_path

    print("RUNNING COMMAND:")
    print(cmd)
    proc = subprocess.Popen(["%s" % cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = proc.stdout.readlines()

    if(result == []):
        print("Error %s" % proc.stderr.readlines())
    else:
        print(result)
        start_server(server_path, server_hostname, server_username, npm_install, run_command)

    return

def start_server(server_path, server_hostname, server_username, npm_install, run_command):
    cmd = "ssh " + server_username +"@"+ server_hostname + " "
    cmd += "\'" + "source ~/.nvm/nvm.sh ; " # TODO: only needed for people who used nvm like me, not sure of a solution...
    cmd += "cd " + server_path + " ; "

    if(npm_install == True):
        # install packages server side before running
        cmd += "npm install" + " ; "
    cmd += run_command + " /'"

    ssh = subprocess.Popen(["%s" % cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    print(result)

def exit_gracefully():
    #Used to send a pkill command to server to stop scripts.
    #However, this functionality is sometimes not desirable. Has been removed for now.
    print("Goodbye!")
    print("Note: Server may still be running.")
    exit()

def signal_handler(signal, frame):
    print('Exiting...')
    exit_gracefully()

if __name__ == "__main__":
    node_modules = False
    npm_install = False
    rsync_del = False
    read_data = False
    run_command = 'node app.js' # defaults to 'node app.js' but changeable through -run_command

    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("--nodemodules", help="Include node modules folder with upload (defaults to false). This isn't recommended, use --npminstall instead when possible (downloads on serverside from package.json file).", action="store_true")
    parser.add_argument("--npminstall", help="Instructs server to download packages from package.json (defaults to false). Include this if you have added a package locally!", action="store_true")
    parser.add_argument("--delete", help="Enables delete functionality in rsync. (If you have deleted a local file, enable this to mirror the change on the server). Be careful with this option.", action="store_true")
    parser.add_argument("-local_path", help="(String) Local path to project '/home/user/node_projct/'")
    parser.add_argument("-server_path", help="(String) Server path to project '/home/user/node_project/'")
    parser.add_argument("-server_hostname", help="(String) Server hostname '123.12.32.123'")
    parser.add_argument("-server_username", help="(String) Server username 'user1'")
    parser.add_argument("-run_command", help="(String) The command to run on the server after upload, defaults to 'node app.js'")
    parser.add_argument("--read", help="Read previous saved data from file.", action="store_true")

    args = parser.parse_args()

    if(args.nodemodules):
        node_modules = True
    if(args.npminstall):
        npm_install = True
    if(args.delete):
        rsync_del = True
    if(args.read):
        read_data = True
        extract_data_file()
        if(user != 0):
            print("printing save file...")
            print("local_path: " + user.local_path)
            print("server_path: " + user.server_path)
            print("server_hostname: " + user.server_hostname)
            print("server_username: " + user.server_username)
            print("run_command: " + user.run_command)
            exit()
    if(args.local_path and args.server_path and args.server_hostname and args.server_username):
        if(args.run_command):
            save_data_file(args.local_path, args.server_path, args.server_hostname, args.server_username, args.run_command)
        else:
            save_data_file(args.local_path, args.server_path, args.server_hostname, args.server_username)
        extract_data_file()
        if(user != 0):
            upload_server(str(user.local_path), str(user.server_path), str(user.server_hostname), str(user.server_username), str(user.run_command), node_modules, npm_install, rsync_del)

    else:
        print("Missing some information! Needs local_path, server_path, server_hostname, and server_username values to run.")
        print("Checking save file for necessary info...")
        extract_data_file()
        if(user != 0):
            print("Save file found!")
            print(user.local_path)
            print(user.server_path)
            print(user.server_hostname)
            print(user.server_username)
            upload_server(str(user.local_path), str(user.server_path), str(user.server_hostname), str(user.server_username), str(user.run_command), node_modules, npm_install, rsync_del)
        else:
            #This shouldn't actually be called, extract_data_file exits if no user found
            exit()
