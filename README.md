# Noder
Noder stands for 'Node Remote', it is a tool for deploying and launching files on a server.

I use it for deploying my local copy of my website to the remote server I host it on.
Noder uses rsync to transfer files, and then sends a modifiable command such as 'node app.js' or 'npm start' to run.

## Getting Started
Download
```
git clone https://github.com/Lasyin/Noder.git
```

Install Prerequisites
```
pip install appdirs
```

(Optional) Symlink to create global shortcut (instead of running 'python noder.py', you can run 'noder')
(MacOS)
```
ln -s /full-path/to-file/Noder/noder.py /usr/local/bin/noder
```

### Prerequisites
* python
* appdirs
* A SSH key to your remote server (Noder does not deal with SSH passwords)

### Running
Run Noder and provide information (replace below information with your information)
```
noder -local_path /Path/To/Local/Project/Folder/ -server_path /Path/To/Server/Project/Folder/ -server_hostname 123.123.123.123 -server_username lasyin -run_command 'npm start'
```

### Arguments
**Required** (Unless already provided and saved)
```
-local_path
```
Provide Noder with the full path to your local folder, this is the parent folder of files you want to transfer to the remote server.

```
-server_path
```
Provide Noder with the full path to your remote folder, this is the parent folder that will be filled with files that you transfer over.

```
-server_hostname
```
Provide Noder with the IP address of your remote server.

```
-server_username
```
Provide Noder with the username of the account you want to log in to on your remote server.

**Optional**
```
-run_command
```
Provide Noder with the command you wish to run after files are transferred. Examples: 'Node app.js', 'npm start'...

```
--npminstall
```
Run 'npm install' after files are transferred, use this if you've installed packages on your local project and want to install them on your remote project.

```
--nodemodules
```
Tell Noder to also transfer the node modules with the rest of your files. This is discouraged, use --npminstall to install packages server side if needed. Transferring node modules takes a long time.

```
--delete
```
By default, Noder uses rsync to transfer files and adds/modifies files, but does not delete them. If you have deleted files locally and want to reflect these changes remotely, use this.

```
--read
```
Noder saves information like local_path, server_path, server_hostname, server_username, and run_command. This is so you do not have to provide information multiple times. To read this saved data, use this.

### Author
Bryan Collins

### Acknowledgments
* Noder uses rsync to transfer files
* Noder uses appdirs to locate cross-platform save directories.
