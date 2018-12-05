from OntologyBuilder import *

import numpy as np 


class HHDataset(object):
	"""docstring for HHDataset"""
	def __init__(self, dataset_name=None,  ontology_builder=None):
		super(HHDataset, self).__init__()
		
		self.ontology_builder = ontology_builder

		if dataset_name is None and ontology_builder is None:
			raise AttributeError("Need to provide either dataset_name or ontology_builder !")
		elif dataset_name is not None and ontology_builder is None:
			if not isinstance(dataset_name, str): 
				raise AttributeError("dataset_name must be a string !")
			else: 
				self.ontology_builder = OntologyBuilder(dataset_name)
		elif ontology_builder is not None:
			if not isinstance(ontology_builder, OntologyBuilder): 
				raise AttributeError("ontology_builder must be an instance of OntologyBuilder !")

		# Assumption : dimension of sensor data is 1 

		self._sensors_typelist = baseOnto.search(subclass_of=Sensor)
		self._sensors_nfeatures = len(self._sensors_typelist)
		self._time_nfeatures = 6
		self.input_nfeatures = self._sensors_nfeatures + self._time_nfeatures

		self._datetime_to_list = lambda date: [date.month, date.day, date.hour, date.minute, date.second, date.microsecond]

	def _time_embedding(self, measurement_list): 
		return np.array(
			[
				self._datetime_to_list(datetime.datetime.strptime(m.timestamp, "%Y-%m-%d %H:%M:%S.%f"))
				for m in measurement_list
			]
		)

	def _data_embedding(self, measurement_list):
		return np.array(
			[
				[
					m.value if m.is_measured_by.is_a[0] == i else 0. 
					for i in self._sensors_typelist
				] 
				for m in measurement_list
			]
		) 

	def _input_embedding(self, measurement_list, normalize=True): 
		data = self._data_embedding(measurement_list)
		time = self._time_embedding(measurement_list)
		input_embedding = np.concatenate((data, time), axis=1)
		if normalize: 
			input_embedding = np.nan_to_num(input_embedding / np.max(np.abs(input_embedding)))
		return input_embedding

	def _events_to_nodes_translmatrix(self, measurement_list): 
		D = np.array(
			[
				[	
					float(m.is_measured_by.is_a[0] == s) 
					for s in self._sensors_typelist
				] 
				for m in measurement_list
			]
		) # Shape (S,M)

		return np.nan_to_num(D / np.sum(D, axis=0)).T # Shape (M,S)

	def get_training_inputs(self, window_size=100, starting_line=0, normalize=True):
		raw_slice = self.ontology_builder.read_training_data(window_size=window_size, starting_line=starting_line)
		I = self._input_embedding(raw_slice['sensor_events'], normalize=normalize)
		D = self._events_to_nodes_translmatrix(raw_slice['sensor_events'])
		return D.dot(I) # ??? Here some attention ? 

	

		









