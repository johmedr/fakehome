import os 
import re
import datetime
from BaseOntology import *


TO_PARSE = [
	'hh10%d'%i for i in range(1,10)
] + [
	'hh11%d'%i for i in range(1,10)
] + [
	'hh12%d'%i for i in range(1,10)
] + [ 
	'hh130'
]

class OntologyBuilder(object): 
	def __init__(data_path, ontology):
		pass 

ROOT_PATH = os.path.abspath('/home/yop/Programmation/Recherche/wsu_datasets/data')



def parse_data(seed): 
	sensors = {}
	base_path = os.path.join(ROOT_PATH, os.path.join(seed, seed))
	sensor_events = []
	activity_events = []

	waiting_activities = {}

	with open(os.path.join(base_path, 'ann.txt')) as ann_file: 
		line_pattern = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)\s([A-Z]{1,2})([A-Z0-9]{3,5})\s([A-Z0-9]+)(\s([A-Za-z].+))?')
		# line_pattern = re.compile('^(.*)\t([A-Z]{1,2})([A-Z0-9]{3,5})\t([A-Z0-9]+)(\t([A-Za-z].+))?.*$')
		activity_pattern = re.compile('([A-Za-z_]+)(=[\",\'](.+)?[\",\'])?.*$')
		for ann_line in ann_file: 
			tokens = line_pattern.search(ann_line)
			timestamp = tokens.group(1)
			name = '%s%s'%(tokens.group(2),tokens.group(3))

			if name not in sensors.keys(): 
				sensors[name] = SENSOR_TYPE_TRANSLATION[tokens.group(2)](tokens.group(3))

			value_str = tokens.group(4).lower()
			value = 0
			if value_str in MEASURE_TYPE_TRANSLATION.keys(): 
				value = float(MEASURE_TYPE_TRANSLATION[value_str])
			else: 
				value = float(value_str)

			sensor_events.append(Measure(sensor=sensors[name], value=value, timestamp=timestamp))

			if tokens.group(6):
				act_tokens = activity_pattern.search(tokens.group(6))
				activity_name = act_tokens.group(1)
				activity_state = None
				
				activity = None

				if act_tokens.group(3): 
					activity_state = act_tokens.group(3).lower() 
					if activity_state == 'end': 
						activity = waiting_activities.pop(activity_name)

				if activity is None: 
					activity = ACTIVITY_TYPE_TRANSLATION[activity_name]()
					
				if activity_state in ACTIVITY_EVENT.keys():
					activity.__setattr__(ACTIVITY_EVENT[activity_state].python_name, timestamp)
				else: 
					raise Warning("Unknown activity state : %s"%(activity_state))

				if activity_state == 'begin': 
					waiting_activities[activity_name] = activity


				activity_events.append(activity)
	return sensors, sensor_events, activity_events, waiting_activities

s,se,ae,wt = parse_data("hh101")