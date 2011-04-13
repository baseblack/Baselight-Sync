#!/usr/bin/env python

import sys; sys.path.append( '%s/../bin/'%sys.path[0] )
import syncbaselight as sync

from shotgun.api.shotgun_api3 import Shotgun
from shotgun.api import keys

class options():
	def __init__(self):
		pass

def test_getProject(project='Extratime Pt 2'):
	sg = Shotgun( keys.url ,"BaselightSync",keys.keys["BaselightSync"] )
	project_id, project_alias = sync.getProject(sg, project)
	
	if not project_id or not project_alias:
		raise

def test_getShot():
	sg = Shotgun( keys.url ,"BaselightSync",keys.keys["BaselightSync"] )
	shot_data = sync.getShot(sg, 2101)
	
	if not shot_data:
		raise
	
def test_getShotStatus():
	sg = Shotgun( keys.url ,"BaselightSync",keys.keys["BaselightSync"] )
	shot_data = sync.getShotStatus(sg, 2101, 74 )
	
	if not shot_data:
		raise

def test_findShotsAndSync_ShotgunAccess(project='Extratime Pt 2'):
	
	opts = options()
	opts.chkdir = False
	opts.sync = False
	opts.copyto = False
	opts.execute = False
	
	(projectid, shots) = sync.findShotsAndSync(project, options=opts )
	
	print projectid
	print shots