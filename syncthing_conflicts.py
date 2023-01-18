#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 6 Nov 2022

@author: George Randolph
"""

import requests
import subprocess
import socket


#API Keys

#Hostname and API Keys for each node
if socket.gethostname() == '':
    api_key = ''
    
elif socket.gethostname() == '':
    api_key = ''

#Get all folder IDs currently being synced
r = requests.get('http://127.0.0.1:8384/rest/config/folders', headers={'X-API-Key':api_key})

#Loop through folder IDs and get human-readable pathnames
for folder in r.json():
    
    path = folder['path']
    
    #Search for any files with "sync-conflict" in them
    cmd = "find '{}' -name '*.sync-conflict-*'".format(path)
    
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    
    #If the output is greater than 0, then there is at least on sync conflict file
    if len(p.stdout.decode()) > 0:
        
        msg = p.stdout.decode()
        
        #Replace the absolute user path with a tilde to condense space in the notification
        try:
            msg = msg.replace('/Users/', '~')
        except:
            continue
        
        #Show a notification for each sync-conflict file.
        cmd = '/usr/local/bin/terminal-notifier -title "SyncThing Conflict" -message "{}" -sender com.github.xor-gate.syncthing-macosx'.format(msg)
        
        p = subprocess.run(cmd, shell=True)