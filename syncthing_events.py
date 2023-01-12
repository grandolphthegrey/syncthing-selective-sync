#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 13:23:02 2022

@author: George Randolph

Script to generate txt files of directory tree and full directory contents to be used for Selective Syncing in SyncThing. On the remote machine, user can use the .txt files to edit .stignore file to enable selective syncing of specific files. A separate LaunchAgent will run this script every minute. This script will then query the specified folders and update the .txt files to reflect the most recent changes (if there have been since the last check)

This file will store the .txt files in a hidden ".selectsync" folder in the root directory.

By default, on the remote machine ALL contents EXCEPT the "*_Directories_Only.txt" and "*_Full_Contents.txt" files are synced

for selective sync directories, the .stignore will have the following default format:
    
    (?d).DS_Store
    Thumbs.db
    desktop.ini
    .Trashes
    .localized
    .Spotlight-V100
    ._*
    
    !/.selectsync/*_Directories_Only*.txt
    !/.selectsync/*_Full_Contents*.txt
    *
    
when you want to start syncing additional folders, add them under the .txt file entry, preceding them with a "!" to tell SyncThing to start sycning them. The "*" at the bottom tells SyncThing to ignore everyting else.
 
"""

import subprocess
import os.path
import requests
import glob
import datetime
import socket


#Global name/variable for all selectsync dirs where .txt files will be saved
selectsyncdir='.selectsync'

#Function to generate .txt file with just directories
def dir_only(my_path, my_file, ignore_dirs=''):
    subprocess.run('/usr/local/bin/tree "`pwd`" {} -Dndtrq -o "{}/{}_Directories_Only.txt"'.format(ignore_dirs, selectsyncdir, my_file), shell=True, cwd=my_path)
    subprocess.run('/usr/local/bin/tree "`pwd`" {} -Dndq -o "{}/{}_Directories_Only_Alphabetical.txt"'.format(ignore_dirs, selectsyncdir, my_file), shell=True, cwd=my_path)

#Function to generate .txt file with all contents
def all_content(my_path, my_file, ignores=''):
    subprocess.run('/usr/local/bin/tree "`pwd`" -I "{}_*.txt" {} -Dntrq -o "{}/{}_Full_Contents.txt" --ignore-case'.format(my_file, ignores, selectsyncdir, my_file), shell=True, cwd=my_path)
    subprocess.run('/usr/local/bin/tree "`pwd`" -I "{}_*.txt" {} -Dnq -o "{}/{}_Full_Contents_Alphabetical.txt" --ignore-case'.format(my_file, ignores, selectsyncdir, my_file), shell=True, cwd=my_path)

#Main function
def main():

    #API Key
    if socket.gethostname() == '':
        api_key = ''
        
    elif socket.gethostname() == '':
        api_key = ''
        
    #number of sync events to query -- may need to tweak this
    lim = 10

    #empty list to store modified folders from SyncThing
    folders = []        

    #Directories to generate Selective Sync Text Files for -- add as needed and update "selective_sync_dirs" and "selective_sync_ids" 
    #NOTE: these will be duplicated and specific to each selective sync folder
    folder_id = ''
    folder_dir = '' #do NOT include the final "/" in the dir path
    folder_ignores = '-I "*.jpg" -I "*.jpeg" -I "*.ini" -I "*.png"'
    
    #Combine to loop through. These directories have to be the same length as the total number of folders being scanned for Selective Syncing. e.g. if we are Selective Syncing "Music" "Photoshop Library" and "Downloads" (3 directories) then the following lists must ALL contain 3 items, in that same order. If only a subset of folders have directory ignore patterns, then fill in the remaining indices with empty strings.
    selective_sync_dirs = [folder_dir]
    selective_sync_ids = [folder_id]
    ignores_array = [folder_ignores]
    ignores_dir_array = [folder_ignores]           
    
    #Get the most recent $lim events from SyncThing
    r = requests.get('http://127.0.0.1:8384/rest/events/disk?since=0&limit={}'.format(str(lim)), headers={'X-API-Key':api_key})
    
    #Reverse the output so that the most recent event is first
    rev_response = list(reversed(r.json()))
    
    for ii, cdir in enumerate(selective_sync_dirs):

        #Directory & File info
        cwd = cdir
        fname = os.path.basename(cwd)
        dir_id = selective_sync_ids[ii]
        
        #Ensure select sync folder exists
        if os.path.exists(cdir+'/'+selectsyncdir) is False:
            os.mkdir(cdir+'/'+selectsyncdir)
        
        #Loop through and get the folder IDs of the last $lim events
        for jj in (range(0,lim)):
            
            folders.append(rev_response[jj]['data']['folder'])
            
        #Check if Selective Sync Directories are among the last $lim LOCAL events that have been changed    
        if dir_id in folders:
            
            #Get mod time from last SyncThing event in Music Folder
            dir_index = folders.index(dir_id)
            mod_time = rev_response[dir_index]['time'][0:16].replace(':','-')
            
            #Verify files exist:
            file_list = glob.glob(cwd+'/'+selectsyncdir+'/'+fname+'_*.txt')    
                
            #If there aren't files, create them: 4 files, then things are working as we expect  
            if len(file_list) == 0 or len(file_list) != 4:
                dir_only(cwd, fname, ignores_dir_array[ii])
                all_content(cwd, fname, ignores_array[ii])
                
            else:
                #Get modified time of txt file
                ftime = datetime.datetime.fromtimestamp(os.path.getmtime(file_list[0]))
                
                #If the modification time of the txt file isn't the same as the last SyncThing event, then update the txt files
                if mod_time != ftime.strftime('%Y-%m-%dT%H-%M'):
                    
                    curr_time = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M')
                    
                    print('shit aint equal on {}, yo. gonna make some new files. Logged this message at {}'.format(cwd, curr_time))
                    dir_only(cwd, fname, ignores_dir_array[ii])
                    all_content(cwd, fname, ignores_array[ii])

if __name__ == "__main__":    
    main()