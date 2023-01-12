# Syncthing Selective Sync Overview
Python script to implement selective syncing with SyncThing `syncthing_events.py` script.

Script to generate txt files of directory tree and full directory contents to be used for Selective Syncing in SyncThing. This script utilizes the Linux `tree` command to generate 4 text files that outline:

* the full contents of a directory, sorted by last modified
* the full contents of a direcotry, sorted alphabetically
* only the subdirectory names (i.e. subfolders only, not individual files) of a directory, sorted by last modified
* only the subdirectory names (i.e. subfolders only, not individual files) of a directory, sorted alphabetically

On the remote machine, user can use the .txt files to edit .stignore file to enable selective syncing of specific files. A separate LaunchAgent will run this script every minute. This script will then query the specified folders and update the .txt files to reflect the most recent changes (if there have been since the last check)

This file will store the .txt files in a hidden ".selectsync" folder in the root directory.

By default, on the remote machine ALL contents EXCEPT the "*_Directories_Only.txt" and "*_Full_Contents.txt" files are synced

for selective sync directories, the .stignore will have the following default format:
    
    (?d).DS_Store
    Thumbs.db
    desktop.ini
    Icon\?
    .Trashes
    .localized
    .Spotlight-V100
    ._*
    
    !/.selectsync/*_Directories_Only*.txt
    !/.selectsync/*_Full_Contents*.txt
    *
    
when you want to start syncing additional folders, add them under the .txt file entry, preceding them with a "!" to tell SyncThing to start sycning them. The "*" at the bottom tells SyncThing to ignore everyting else.

## API Keys

Each node will have its own API key. The first lines of `main` will need to be edited with the appropriate hostname and API key for each node.

## Folder IDs

Each folder that will be selectively synced will have its own folder ID. The lines below the API keys and host names will need to be modified to with the appropriate folder IDs and paths of where the sync folder resides. **NOTE** this script assumes the paths for the synced folders are the same. If the paths are different on each node, then the paths will have to be changed on each node where the script runs.

## LaunchAgent

To get this script to automatically use the `syncthing_events.plist` file as a template. This launch agent file will specify the Python script to run every minute and when changes are detected in any of the monitored folders (specified in the **Folder ID** section above) the script will re-generate the txt files of the direcotry structure and contents.

## Example

User wants to selectively sync the contents of `~/Music`

This script will create the following .txt files:
* `~/Music/.selectsync/Music_Directories_Only_Alphabetical.txt`
* `~/Music/.selectsync/Music_Directories_Only.txt`
* `~/Music/.selectsync/Music_Full_Contents_Alphabetical.txt`
* `~/Music/.selectsync/Music_Full_Contents.txt`

Users can then edit the .stignore patterns by looking at the contents of the .txt files to determine what information to be selectively sync'ed to the node.
