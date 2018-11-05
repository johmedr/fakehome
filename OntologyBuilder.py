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

ROOT_PATH = os.path.abspath('/home/yop/Programmation/Recherche/wsu_datasets/data')

class OntologyBuilder(object): 
	def __init__(self, dataset_name="hh101"):
		self.dataset_name = dataset_name
		self.dataset_path = os.path.join(ROOT_PATH, os.path.join(dataset_name, dataset_name))

		def extract_sensor_list(): 
			sensors = {}

			with open(os.path.join(self.dataset_path, 'ann.txt')) as ann_file: 
				line_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+\s([A-Z]{1,2})([A-Z0-9]{3,5})*')

				for ann_line in ann_file: 
					tokens = line_pattern.search(ann_line)

					if not tokens: 
						raise Warning("Unable to find data pattern on line %s"%ann_line)

					name = tokens.group(1) + tokens.group(2)

					if name not in sensors.keys(): 
						with onto:
							sensors[name] = SENSOR_TYPE_TRANSLATION[tokens.group(1)](tokens.group(2))

			return sensors

		self.sensors = extract_sensor_list()

		with open(os.path.join(self.dataset_path, 'ann.txt')) as ann_file: 
			self.ann_file_length = len(ann_file.readlines())

		with open(os.path.join(self.dataset_path, 'rawdata.txt')) as rawdata_file: 
			self.rawdata_file_length = len(rawdata_file.readlines())



	def read_training_measures(self, starting_line=0, window_size=-1): 
		sensor_events = []
		activity_events = []

		waiting_activities = {}

		with open(os.path.join(self.dataset_path, 'ann.txt')) as ann_file: 
			line_pattern = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)\s([A-Z]{1,2})([A-Z0-9]{3,5})\s([A-Z0-9]+)(\s([A-Za-z].+))?')
			activity_pattern = re.compile('([A-Za-z_]+)(=[\",\'](.+)?[\",\'])?.*$')

			if window_size == -1: 
				ann_lines = ann_file.readlines()[starting_line:]
			elif starting_line + window_size > self.ann_file_length: 
				ann_lines = ann_file.readlines()[starting_line:]
				raise Warning("Trying to read %d lines, but annotated data file contains %d lines."%(starting_line + window_size, self.ann_file_length))
			else: 
				ann_lines = ann_file.readlines()[starting_line:starting_line+window_size]

			for ann_line in ann_lines: 
				tokens = line_pattern.search(ann_line)

				timestamp = tokens.group(1)
				name = '%s%s'%(tokens.group(2),tokens.group(3))

				value_str = tokens.group(4).lower()
				value = 0
				if value_str in MEASURE_TYPE_TRANSLATION.keys(): 
					value = float(MEASURE_TYPE_TRANSLATION[value_str])
				else: 
					value = float(value_str)

				sensor_events.append(Measure(sensor=self.sensors[name], value=value, timestamp=timestamp))

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

		return sensor_events, activity_events, waiting_activities 

if __name__ == "__main__":
	o = OntologyBuilder()