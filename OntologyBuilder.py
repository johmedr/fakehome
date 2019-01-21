import os
import re
from .BaseOntology import *
from .HHStaticConf import *


TO_PARSE = [
    'hh10%d' % i for i in range(1, 10)
] + [
    'hh11%d' % i for i in range(1, 10)
] + [
    'hh12%d' % i for i in range(1, 10)
] + [
    'hh130'
]

ROOT_PATH = os.path.abspath(
    '/home/yop/Programmation/Recherche/wsu_datasets/data')


class Datasets:
    hh101 = 'hh101'
    hh102 = 'hh102'
    hh103 = 'hh103'


class OntologyBuilder(object):

    def __init__(self, data_path=ROOT_PATH, dataset_name=Datasets.hh101):
        super(OntologyBuilder, self).__init__()

        self.dataset_name = dataset_name
        self.dataset_path = os.path.join(
            data_path, os.path.join(self.dataset_name, self.dataset_name))

        try:
            self.dataset_conf = datasets_confs[self.dataset_name]
        except KeyError:
            raise NotImplementedError(
                "OntologyBuilder not implemented for {}.".format(self.dataset_name))

        self.anndata_filepath = os.path.join(self.dataset_path, 'ann.txt')
        self.rawdata_filepath = os.path.join(self.dataset_path, 'rawdata.txt')

        with open(self.anndata_filepath) as file:
            self.ann_file_length = len(file.readlines())

        with open(self.rawdata_filepath) as file:
            self.rawdata_file_length = len(file.readlines())

        self.working_ontology = get_ontology(os.path.join(
            self.dataset_path, self.dataset_name + ".owl"))

        with self.working_ontology:
            # Create locations entities
            self.locations = {}
            for l in self.dataset_conf['locations']:
                self.locations[l] = LOCATION_TYPE_TRANSLATION[l]()

            for (loc, instance) in self.locations.items():
                try:
                    for other in self.dataset_conf['locations_adjacency'][loc]:
                        other_instance = self.locations[other]
                        instance.is_adjacent_to.append(other_instance)
                        other_instance.is_adjacent_to.append(instance)
                except KeyError as e:
                    print('Get key error: {}. Continuing.'.format(e))

            #
            self.sensors = {}
            for sensor_name, location in self.dataset_conf['sensors_locations'].items():
                type_pattern = re.compile('([A-Z]{1,2})[0-9]+')
                sensor_type = type_pattern.search(sensor_name).group(1)
                self.sensors[sensor_name] = SENSOR_TYPE_TRANSLATION[
                    sensor_type](name=sensor_name, has_location=self.locations[location])

        self.training_slice = None
        self.testing_slice = None

    def read_training_data(self, window_size=-1, starting_line=0):
        with self.working_ontology:

            if self.training_slice is not None:
                if starting_line == self.training_slice['start'] and starting_line + window_size == self.training_slice['stop']:
                    return self.training_slice

                else:
                    for i in self.training_slice['sensor_events']:
                        destroy_entity(i)
                    for i in self.training_slice['activity_events']:
                        destroy_entity(i)
            else:
                self.training_slice = {}

            sensor_events = []
            activity_events = []

            waiting_activities = {}

            with open(self.anndata_filepath) as file:
                line_pattern = re.compile(
                    '^([0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)\s([A-Z]{1,2})([A-Z0-9]{3,5})\s([A-Z0-9]+)(\s([A-Za-z].+))?')
                activity_pattern = re.compile(
                    '([A-Za-z_]+)(=[\",\'](.+)?[\",\'])?.*$')

                if window_size == -1:
                    lines = file.readlines()[starting_line:]
                elif starting_line + window_size > self.ann_file_length:
                    lines = file.readlines()[starting_line:]
                    raise Warning("Trying to read %d lines, but annotated data file contains %d lines." % (
                        starting_line + window_size, self.ann_file_length))
                else:
                    lines = file.readlines()[
                        starting_line:starting_line + window_size]

                for line in lines:
                    tokens = line_pattern.search(line)

                    timestamp = tokens.group(1)
                    name = '%s%s' % (tokens.group(2), tokens.group(3))

                    value_str = tokens.group(4).lower()
                    value = 0
                    if value_str in MEASURE_TYPE_TRANSLATION.keys():
                        value = float(MEASURE_TYPE_TRANSLATION[value_str])
                    else:
                        value = float(value_str)

                    sensor_events.append(Measure(is_measured_by=self.sensors[
                                         name], value=value, timestamp=timestamp))

                    if tokens.group(6):
                        act_tokens = activity_pattern.search(tokens.group(6))
                        activity_name = act_tokens.group(1)
                        activity_state = None

                        activity = None

                        if act_tokens.group(3):
                            activity_state = act_tokens.group(3).lower()
                            if activity_state == 'end':
                                activity = waiting_activities.pop(
                                    activity_name)

                        if activity is None:
                            activity = ACTIVITY_TYPE_TRANSLATION[
                                activity_name]()

                        if activity_state in ACTIVITY_EVENT.keys():
                            activity.__setattr__(
                                ACTIVITY_EVENT[activity_state].python_name, timestamp)
                        else:
                            raise Warning(
                                "Unknown activity state : %s" % (activity_state))

                        if activity_state == 'begin':
                            waiting_activities[activity_name] = activity

                        activity_events.append(activity)

            self.training_slice['start'] = starting_line
            self.training_slice['stop'] = starting_line + window_size
            self.training_slice['sensor_events'] = sensor_events
            self.training_slice['activity_events'] = activity_events
            self.training_slice['waiting_activities'] = waiting_activities

            return self.training_slice

    def read_testing_data(self, window_size=-1, starting_line=0):
        with self.working_ontology:

            if self.testing_slice is not None:
                if starting_line == self.testing_slice['start'] and starting_line + window_size == self.testing_slice['stop']:
                    return self.testing_slice
                else:
                    for i in self.testing_slice['sensor_events']:
                        destroy_entity(i)
            else:
                self.testing_slice = {}

            sensor_events = []

            with open(self.rawdata_filepath) as file:
                line_pattern = re.compile(
                    '^([0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)\s([A-Z]{1,2})([A-Z0-9]{3,5})\s([A-Z0-9]+)(\s([A-Za-z].+))?')

                if window_size == -1:
                    lines = file.readlines()[starting_line:]
                elif starting_line + window_size > self.rawdata_file_length:
                    lines = file.readlines()[starting_line:]
                    raise Warning("Trying to read %d lines, but annotated data file contains %d lines." % (
                        starting_line + window_size, self.rawdata_file_length))
                else:
                    lines = file.readlines()[
                        starting_line:starting_line + window_size]

                for line in lines:
                    tokens = line_pattern.search(line)

                    timestamp = tokens.group(1)
                    name = '%s%s' % (tokens.group(2), tokens.group(3))

                    value_str = tokens.group(4).lower()
                    value = 0
                    if value_str in MEASURE_TYPE_TRANSLATION.keys():
                        value = float(MEASURE_TYPE_TRANSLATION[value_str])
                    else:
                        value = float(value_str)

                    sensor_events.append(Measure(is_measured_by=self.sensors[
                                         name], value=value, timestamp=timestamp))

            self.testing_slice['start'] = starting_line
            self.testing_slice['stop'] = starting_line + window_size
            self.testing_slice['sensor_events'] = sensor_events

            return self.testing_slice

if __name__ == "__main__":
    o = OntologyBuilder()
