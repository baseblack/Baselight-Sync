Baselight-Sync
==============

sync-baselight.py - provides an interface between shotgun and the baselight to run periodic syncs of /mnt/disk1/images1 and /mnt/muxfs 
                              In the current build the shotgun server is directly interegated each time this script is run. A proxy would help reduce the
			      overhead that this induces.

version = 1.0.0

***

## To Use:

crontab for this script:

0 9 * * * python /usr/local/bin/syncbaselight.py    # once a day at 9am

crontab for  baselight-sync.sh:

0 * * * * bash /var/tmp/baselight-sync.sh    # once every hour on the hour

***

## Options

Usage: syncbaselight.py [options]

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --project=PROJECTNAME
                        name of the project in shotgun
  --chkdir              check that directories exist on baselight
  --no-chkdir           (default) do not check that directories exist on
                        baselight
  --sync                perform sync between shared storage and baselight
  --no-sync             (default) do not perform sync between shared storage
                        and baselight
  --copy                (default) copy the shell scripts to execute to the
                        baselight
  --no-copy             dry run of copy of sync/check lists to baselight
  --exec                use ssh to execute the shell scripts on the baselight
  --no-exec             dry run of check/sync

