from ..core import DatasetObject
from ..core import BaseOntology

import json
import logging
import re

import sys


def str2ontoclass(str):
    getattr(sys.modules[BaseOntology], str)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class HHDatasetObject(DatasetObject):

    def __init__(
            self, dataset_name="hh101", config_file="hh_dataset_conf.json"):

        self.dataset_name = dataset_name
        with open(config_file, 'r') as f:
            logging.debug("Reading json config file '%s'...", config_file)
            self.dataset_conf = json.load(f)

        try:
            logging.debug("Extracting dataset '%s'...", dataset_name)
            self.dataset_conf = self.dataset_conf[self.dataset_name]
        except KeyError as e:
            logging.error("Cannot find dataset with name: '%s'", dataset_name)
            raise e

        # TODO Check config file structure
        if self.dataset_conf["ontoref"] != "BaseOntology":
            logging.error("Cannot handle different ontologies.")
            raise NotImplementedError("Cannot handle different ontologies.")

        self.sensor_type_pattern = re.compile('([A-Z]{1,2})[0-9]+')
        self.line_pattern = re.compile(
            '^([0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]+)\s([A-Z]{1,2})([A-Z0-9]{3,5})\s([A-Z0-9]+)(\s([A-Za-z].+))?')
        self.activity_pattern = re.compile(
            '([A-Za-z_]+)(=[\",\'](.+)?[\",\'])?.*$')

        self._sensor_list = []
        for sensors in self.dataset_conf["sensors"]["locations"].values():
            self._sensor_list += sensors

    def sensor_name_mapping(
            self, sensor_name_str):
        """ sensor_type_mapping()
                Takes the sensor name as a string extracted from the data file.
                Returns the associated type to build the ontology with.

                If the sensor name contains information about its type, using regex and lookup table can be the simplest way to implement this function.

                Example:

                dataset_object.sensor_type_mapping('LS') returns LightSensorType.
        """
        sensor_type = self.sensor_type_pattern.search(sensor_name_str).group(1)
        try:
            return str2ontoclass(self.dataset_conf['sensors']['type'][sensor_type])
        except KeyError as e:
            s = "Cannot find sensor type for sensor with name '%s'" % (
                sensor_name_str,)
            logging.error(s)
            raise KeyError(s)

    def sensor_state_mapping(
            self, sensor_state_str):
        """ sensor_state_mapping()
                Takes the sensor state as a string extracted from the data file.
                Returns the desired value that will be used to create the Measure instance. That type must be convertible to a float.

                Example:

                dataset_object.sensor_state_mapping('ON') returns 1
        """
        try:
            return str2bool(
                self.dataset_conf['sensors']['state'][sensor_state_str])
        except KeyError as e:
            s = "Cannot find sensor state for state '%s'" % (
                sensor_state_str,)
            logging.error(s)
            raise KeyError(s)

    def activity_type_mapping(
            self, activity_type_str):
        """ activity_type_mapping()
                Takes the activity type as a string extracted from the data file.
                Returns the associated type to build the ontology with.

                Example:

                dataset_object.activity_type_mapping('cooking') returns CookingActivity.
        """
        try:
            return str2ontoclass(self.dataset_conf['activities']['type'][activity_type_str])
        except KeyError as e:
            s = "Cannot find activity type for activity with name '%s'" % (
                activity_type_str,)
            logging.error(s)
            raise KeyError(s)

    def activity_state_mapping(
            self, activity_state_str):
        """ activity_state_mapping()
                Takes the activity state as a string extracted from the data file.
                Returns the type of relation to build for this state.
                Please note that the relation type must take a timestamp as an argument.

                Example:

                dataset_object.activity_state_mapping('begins') returns beginsAt
        """
        try:
            return str2ontoclass(self.dataset_conf['activities']['state'][activity_state_str])
        except KeyError as e:
            s = "Cannot find activity state for state '%s'" % (
                activity_state_str,)
            logging.error(s)
            raise KeyError(s)

    def location_name_mapping(
            self, location_name_str):
        """ location_type_mapping()
                Takes the location name as a string extracted from the data file.
                Returns the associated type to build the ontology with.

                If the location name contains information about its type, using regex and lookup table can be the simplest way to implement this function.

                Example:

                dataset_object.location_type_mapping('bedroom') returns BedroomLocation.
        """
        try:
            return str2ontoclass(self.dataset_conf['locations']['type'][location_name_str])
        except KeyError as e:
            s = "Cannot find location type for location with name '%s'" % (
                location_name_str,)
            logging.error(s)
            raise KeyError(s)

    def apply_line_pattern(self, line):
        """ apply_line_pattern
                Takes a line from the data file as argument. 
                Returns a dict containing the following keys:
                    'sensor': the sensor name, 
                    'state': the sensor state or value (as a string)
                    'activity': the corresponding activity or None, 
                    'activity_state': the corresponding activity state or None

                Using regex can be the simplest way to implement this function.
        """
        extracted = {}
        tokens = self.line_pattern.search(line)

        extracted['timestamp'] = tokens.group(1)
        extracted['sensor'] = '%s%s' % (tokens.group(2), tokens.group(3))
        extracted['state'] = tokens.group(4).lower()
        extracted['activity'] = None
        extracted['activity_state'] = None

        if tokens.group(6):
            act_tokens = self.activity_pattern.search(tokens.group(6))

            extracted['activity'] = act_tokens.group(1)

            if act_tokens.group(3):
                extracted['activity_state'] = act_tokens.group(3).lower()

        return extracted

    @property
    def sensor_list(self):
        """ Property: sensor_list
                Returns the list of sensors used in the dataset. 
        """
        return self._sensor_list

    @property
    def activity_list(self):
        """ Property: activity_list
                Returns the list of activities used in the dataset. 
        """
        return list(self.dataset_conf['activities']['type'].keys())

    @property
    def location_list(self):
        """ Property: location_list
                Returns the list of locations used in the dataset. 
        """
        return list(self.dataset_conf['locations']['type'].keys())

    @property
    def filepath(self):
        """ Property: filepath
                Returns the absolute path to the data file. 
        """
        return self.dataset_conf['datapath']

    @property
    def name(self):
        """ Property: name
                Returns the name of the dataset.
        """
        return self.dataset_name
