#!/usr/bin/env python

"""
sync-baselight.py - provides an interface between shotgun and the baselight to run periodic syncs of /mnt/disk1/images1 and /mnt/muxfs 
                              In the current build the shotgun server is directly interegated each time this script is run. A proxy would help reduce the
			      overhead that this induces.i
			      
crontab for this script:

0 9 * * * python /usr/local/bin/syncbaselight.py    # once a day at 9am

crontab for  baselight-sync.sh:

0 * * * * bash /var/tmp/baselight-sync.sh    # once every hour on the hour
			      
"""

import sys
import os
import subprocess 

from shotgun import application as sgApp 

__version__ = "1.0.0"

##########################################################
#
# Baselight functions. These connect to the baselight and execute commands on it via ssh
#
##########################################################

def baselightCheckDirectories( project, shots, copyto=True, execute=False ):
	"""Ensures that all of the directories needed to sync between on the baselight exist on the local disk.
	Compiles a list of directories to check for the existance of. If they do not exist the full path with any 
	intermediate directories is made.
	
	Commands are executed in serial on the baselight to prevent locking on its db.
	"""	
	
	commands = ["#!/usr/bin/env sh -x","\n"]
		
	for shot in shots.keys():
		sequence = shots[shot].split('_')[0]
		
		baselight_indir   =  "/mnt/disk1/images1/%s/%s/%s/" % ( project, sequence,  shot )
		baselight_outdir = "/mnt/disk1/images1/%s/%s/%s/"  % ( project, sequence,  shot )
	
		commands.append( '[ -e %s ] || mkdir -p %s;\n' % (baselight_indir  , baselight_indir  ) )
		commands.append( '[ -e %s ] || mkdir -p %s;\n' % (baselight_outdir, baselight_outdir) )	
	
	f = open('/tmp/baselight-dircheck.sh', 'w')
	f.writelines( commands )
	f.close()

	if copyto:
		p = subprocess.Popen("scp /tmp/baselight-dircheck.sh filmlight@baselight-1:/var/tmp/", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		if os.waitpid(p.pid, 0)[1]:
			print "ERROR %s" % p.stdout
			sys.exit(1)
		
	if execute:	
		print "Checking directories on 'baselight-1'"
		p = subprocess.Popen("ssh filmlight@baselight-1 bash -x /var/tmp/baselight-dircheck.sh" , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for msg in p.stdout:
			print msg
			sys.stdout.flush()
			
		
def baselightSyncDirectories( project, shots, copyto=True, execute=False  ):	
	"""Takes the list of shots which are currently in progress and builds a bash script of fl-cp commands. 
	Each command syncs either the IN or OUT directory for a shot and all of the directories beneath it. 
	If a user puts a stupid directory in there which simply shouldn't be then it will be copied across. There 
	is no vetting.
	"""

	commands = ["#!/usr/bin/env sh -x","\n"]
	
	shotnames = shots.keys()
	shotnames.sort()
	for shot in shotnames:
		sequence = shots[shot].split('_')[0]

		baselight_indir   =  "/mnt/disk1/images1/%s/%s/%s/" % ( project, sequence,  shot )
		baselight_outdir = "/mnt/disk1/images1/%s/%s/%s/"  % ( project, sequence,  shot )
		
		mux_indir = "/mnt/muxfs/%s/%s/%s/IN/"     % ( project, sequence, shot )
		mux_outdir = "/mnt/muxfs/%s/%s/%s/OUT/" % ( project, sequence, shot )
					
		commands.append( 'fl-cp -sync %s %s;\n' % (mux_indir  , baselight_indir  ) )
		commands.append( 'fl-cp -sync %s %s;\n' % (mux_outdir, baselight_outdir) )
					
	f = open('/tmp/baselight-sync.sh', 'w')
	f.writelines( commands )
	f.close()
	
	if copyto:
		p = subprocess.Popen("scp /tmp/baselight-sync.sh filmlight@baselight-1:/var/tmp/", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		if os.waitpid(p.pid, 0)[1]:
			print "ERROR %s" % p.stdout
			sys.exit(1)
			
	if execute:		
		print "Syncing directories on 'baselight-1'"
		p = subprocess.Popen("ssh filmlight@baselight-1 bash -x /var/tmp/baselight-sync.sh" , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for msg in p.stdout:
			print msg
			sys.stdout.flush()

##########################################################
#
# The main func
#
##########################################################

def findShotsAndSync(project='Template Project', options=None ):
	"""Requests information about the provided project name. Uses the project id to filter a search for sequences
	which are currently in an 'In Progress' state. For each sequence searches for the list of 'In Progress' shots it is
	composed of. Each of these is added to a list of shots to be sync'd to the baselight.
	"""
	
	shotsInProgress = {}
	
	print "Connecting to Shotgun server..."
	sg = sgApp.newShotgunConnection( 'BaselightSync' )
		
	print "Retrieving Project data..."
	project_id, project_alias = sgApp.getProject( sg, project )
		
	print "Retrieving sequences..."
	sequence_data = sgApp.getSequences( sg, project_id )
	
	print "Checking for shots currently 'In progress' (this may take a few minutes):"	
	for sequence in sequence_data:
		for shot in sequence['shots']:
			if sgApp.getShotStatus( sg, shot['id'], project_id ) == 'In Progress':
				print shot['name'], 'In Progress'
			
				shotsInProgress[ shot['name'] ] = sequence['code']

	if options.chkdir:
		baselightCheckDirectories( project_alias, shotsInProgress, options.copyto, options.execute )
	if options.sync:
		baselightSyncDirectories( project_alias, shotsInProgress, options.copyto, options.excute )
		
	return project_alias, shotsInProgress

def main():
	import optparse    
	
	optparser = optparse.OptionParser( version=__version__, usage="%prog [options]" )

	optparser.disable_interspersed_args() #unix style cli

	optparser.add_option("--project", dest="projectname", type="string", default='', help="name of the project in shotgun" )

	optparser.add_option("--chkdir", action="store_true", dest="chkdir", default=False, help="check that directories exist on baselight" )
	optparser.add_option("--no-chkdir", action="store_false", dest="chkdir", help="(default) do not check that directories exist on baselight" )
	optparser.add_option("--sync", action="store_true", dest="sync", default=False, help="perform sync between shared storage and baselight" )
	optparser.add_option("--no-sync", action="store_false", dest="chkdir", help="(default) do not perform sync between shared storage and baselight" )

	optparser.add_option("--copy", action="store_true", dest="copyto", default=True, help="(default) copy the shell scripts to execute to the baselight" )
	optparser.add_option("--no-copy", action="store_false", dest="copyto", help="dry run of copy of sync/check lists to baselight" )
	optparser.add_option("--exec", action="store_true", dest="execute", default=False, help="use ssh to execute the shell scripts on the baselight" )
	optparser.add_option("--no-exec", action="store_false", dest="execute", help="dry run of check/sync" )

	options, args = optparser.parse_args()

	if options.projectname:
		findShotsAndSync(  options.projectname, options )
	else:
		print "Please provide a project name, eg --project='Template Project'"

if __name__ == "__main__":
    main()	#optparse conflicts with nosetests if left in the main body and imported as a module in a test.
