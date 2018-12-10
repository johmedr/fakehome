import os 
import re
import numpy as np

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

MEASURE_TYPE_TRANSLATION = {
    'open': 1, 
    'close': 0, 
    'on': 1, 
    'off': 0
}


ACTIVITY_LIST = [
    "Bathe",
    "Bed_Toilet_Transition",
    "Caregiver",
    "Cook",
    "Cook_Breakfast",
    "Cook_Dinner",
    "Cook_Lunch",
    "Dress",
    "Drink",
    "Drug_Management",
    "Eat",
    "Eat_Breakfast",
    "Eat_Dinner",
    "Eat_Lunch",
    "Enter_Home",
    "Entertain_Guests",
    "Evening_Meds",
    "Exercise",
    "Housekeeping",
    "Groceries",
    "Groom",
    "Laundry",
    "Leave_Home",
    "Make_Bed",
    "Morning_Meds",
    "Paramedics",
    "Personal_Hygiene",
    "Phone",
    "Piano",
    "Cook_Breakfast",
    "Dishes", # CHANGED
    "Dress",
    "Groom",
    "Relax",
    "Sleep",
    "Toilet",
    "Work",
    "Read",
    "Relax",
    "Sleep",
    "Sleep_Out_Of_Bed",
    "Step_Out",
    "Take_Medicine",
    "Toilet",
    "Wash_Breakfast_Dishes",
    "Wash_Dinner_Dishes",
    "Wash_Dishes",
    "Wash_Lunch_Dishes",
    "Watch_TV", # CHANGED
    "Work",
    "Work_At_Desk",
    "Work_At_Table",
    "Work_On_Computer"
]


class SimpleDataFetcher(object): 
	def __init__(self, data_path=ROOT_PATH, dataset_name="hh101"):
		super(SimpleDataFetcher, self).__init__()

		self.dataset_name = dataset_name
		self.dataset_path = os.path.join(data_path, os.path.join(dataset_name, dataset_name))

		self.anndata_filepath = os.path.join(self.dataset_path, 'ann.txt')
		self.rawdata_filepath = os.path.join(self.dataset_path, 'rawdata.txt')

		with open(self.anndata_filepath) as file: 
			self.ann_file_length = len(file.readlines())

		with open(self.rawdata_filepath) as file: 
			self.rawdata_file_length = len(file.readlines())


		def extract_sensor_list(): 
			sensors_typedict = {}
			sensors_dict = {}
			sensors_nb = 0

			with open(self.anndata_filepath) as file: 
				line_pattern = re.compile('^[0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+\s([A-Z]{1,2})([A-Z0-9]{3,6})*')

				for line in file: 
					tokens = line_pattern.search(line)

					if not tokens: 
						raise Warning("Unable to find data pattern on line %s"%line)

					name = tokens.group(1) + tokens.group(2)

					if name not in sensors_dict.keys(): 
						sensors_typedict[name] = tokens.group(1)
						sensors_dict.update({name:sensors_nb})
						sensors_nb += 1

			return sensors_dict, sensors_typedict, sensors_nb + 1

		self.sensors_dict, self.sensors_typedict	, self.sensors_nb = extract_sensor_list()

		self.activity_nb = len(ACTIVITY_LIST)
		self.activity_dict= {ACTIVITY_LIST[i]:i for i in range(self.activity_nb)}

		self.waiting_activities = set()

	def read_annotated_data(self, window_size=-1, starting_line=0): 
		if window_size == -1: 
			temporal_win = self.ann_file_length
		else: 
			temporal_win = window_size

		sensor_events = np.zeros((self.sensors_nb, temporal_win))
		activity_events = np.zeros((self.activity_nb + 1, temporal_win))


		with open(self.anndata_filepath) as file: 
			line_pattern = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)\s([A-Z]{1,2})([A-Z0-9]{3,5})\s([A-Z0-9]+)(\s([A-Za-z].+))?')
			activity_pattern = re.compile('([A-Za-z_]+)(=[\",\'](.+)?[\",\'])?.*$')

			if window_size == -1: 
				lines = file.readlines()[starting_line:]
			elif starting_line + window_size > self.ann_file_length: 
				lines = file.readlines()[starting_line:]
				raise Warning("Trying to read %d lines, but annotated data file contains %d lines."%(starting_line + window_size, self.ann_file_length))
			else: 
				lines = file.readlines()[starting_line:starting_line+window_size]

			line_num = 0
			for line in lines: 
				tokens = line_pattern.search(line)

				#timestamp = tokens.group(1)
				name = '%s%s'%(tokens.group(2),tokens.group(3))

				value_str = tokens.group(4).lower()
				value = 0

				if value_str in MEASURE_TYPE_TRANSLATION.keys(): 
					value = float(MEASURE_TYPE_TRANSLATION[value_str])
				else: 
					value = float(value_str)

				# Event = 1-hot valued vector   
				if line_num > 0: 
					sensor_events[:, line_num] = sensor_events[:, line_num - 1] 
				sensor_events[self.sensors_dict[name], line_num] = value

				if tokens.group(6):
					act_tokens = activity_pattern.search(tokens.group(6))
					activity_name = act_tokens.group(1)
					activity_state = None

					if act_tokens.group(3): 
						activity_state = act_tokens.group(3).lower() 
						if activity_state == 'end' and activity_name in self.waiting_activities: 

							self.waiting_activities.remove(activity_name)

						elif activity_state == 'begin':
							self.waiting_activities.add(activity_name)

						else:

							self.waiting_activities.add(activity_name)
							raise Warning("Unseen activity '%s'"%activity_name)

					else: 
						activity_events[self.activity_dict[activity_name], line_num] = 1

				for name in self.waiting_activities: 
					activity_events[self.activity_dict[name], line_num] = 1
				if activity_events[:, line_num].sum() == 0: 
					activity_events[-1, line_num] = 1
					

				line_num += 1

			return sensor_events, activity_events

	# def read_testing_data(self, window_size=-1, starting_line=0): 
	# 	with self.working_ontology:

	# 		if self.testing_slice is not None: 
	# 			if starting_line == self.testing_slice['start'] and starting_line + window_size == self.testing_slice['stop']: 
	# 				return self.testing_slice
	# 			else:
	# 				for i in self.testing_slice['sensor_events']: 
	# 					destroy_entity(i)
	# 		else: 
	# 			self.testing_slice = {}

	# 		sensor_events = []

	# 		with open(self.rawdata_filepath) as file: 
	# 			line_pattern = re.compile('^([0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)\s([A-Z]{1,2})([A-Z0-9]{3,5})\s([A-Z0-9]+)(\s([A-Za-z].+))?')

	# 			if window_size == -1: 
	# 				lines = file.readlines()[starting_line:]
	# 			elif starting_line + window_size > self.rawdata_file_length: 
	# 				lines = file.readlines()[starting_line:]
	# 				raise Warning("Trying to read %d lines, but annotated data file contains %d lines."%(starting_line + window_size, self.rawdata_file_length))
	# 			else: 
	# 				lines = file.readlines()[starting_line:starting_line+window_size]

	# 			for line in lines: 
	# 				tokens = line_pattern.search(line)

	# 				timestamp = tokens.group(1)
	# 				name = '%s%s'%(tokens.group(2),tokens.group(3))

	# 				value_str = tokens.group(4).lower()
	# 				value = 0
	# 				if value_str in MEASURE_TYPE_TRANSLATION.keys(): 
	# 					value = float(MEASURE_TYPE_TRANSLATION[value_str])
	# 				else: 
	# 					value = float(value_str)

	# 				sensor_events.append(Measure(is_measured_by=self.sensors[name], value=value, timestamp=timestamp))

	# 		self.testing_slice['start'] = starting_line
	# 		self.testing_slice['stop'] = starting_line + window_size
	# 		self.testing_slice['sensor_events'] = sensor_events

	# 		return self.testing_slice
