from ..core import DatasetObject
from ..core.BaseOntology import *

import json
import re
import sys
import os

import logging
logger = logging.getLogger(__name__)


def str2ontoclass(string):
    try:
        return getattr(sys.modules[__name__], string)
    except TypeError as e:
        s = "Wrong attribute type for str2ontoclass: must be a string, but get %s." % (
            string,)
        logger.error(s)
        raise TypeError(s)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '.config', "hh_datasets_config.json")


class HHDataset(DatasetObject):

    def __init__(
            self, dataset_name, config_file=DEFAULT_CONFIG_FILE):

        self.dataset_name = dataset_name
        with open(config_file, 'r') as f:
            logger.debug("Reading json config file '%s'...", config_file)
            self.dataset_conf = json.load(f)

        logger.debug(
            "Extracting dataset configuration for '%s'...", dataset_name)
        try:
            self.dataset_conf = self.dataset_conf[self.dataset_name]
        except KeyError as e:
            logger.error("Cannot find dataset with name: '%s'", dataset_name)
            raise e

        # TODO Check config file structure
        if self.dataset_conf["ontoref"] != "BaseOntology":
            s = "Cannot handle different ontologies."
            logger.error(s)
            raise NotImplementedError(s)

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
            logger.error(s)
            raise KeyError(s)

    def _sensor_type_mapping(
            self, sensor_type_str):
        try:
            return str2ontoclass(self.dataset_conf['sensors']['type'][sensor_type_str])
        except KeyError as e:
            s = "Cannot find sensor type for sensor of type '%s'" % (
                sensor_type_str,)
            logger.error(s)
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
            return float(sensor_state_str)
        except ValueError:
            pass
        try:
            return str2bool(
                self.dataset_conf['sensors']['state'][sensor_state_str])
        except KeyError as e:
            s = "Cannot find sensor state for state '%s', which cannot be converted to float..." % (
                sensor_state_str,)
            logger.error(s)
            raise ValueError(s)

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
            logger.debug(s)
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
        if activity_state_str is None:
            activity_state_str = 'None'
        try:
            return str2ontoclass(self.dataset_conf['activities']['state'][activity_state_str])
        except KeyError as e:
            s = "Cannot find activity state for state '%s'" % (
                activity_state_str,)
            logger.debug(s)
            raise KeyError(s)

    def location_type_mapping(
            self, location_name_str):
        """ location_type_mapping()
                Takes the location name as a string.
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
            logger.error(s)
            raise KeyError(s)

    def get_location_adjacency(
            self, location_name_str):
        """ get_location_adjacency()
                Takes the location name as a string.
                Returns the list of adjacent locations to build the ontology with.

                Example:

                dataset_object.get_location_adjacency('bedroom') returns ['living_room', 'bathroom1'].
        """
        try:
            return list(self.dataset_conf['locations']['adjacency'][location_name_str])
        except KeyError as e:
            s = "Cannot find location adjacency for location with name '%s'" % (
                location_name_str,)
            logger.debug(s)
            return []

    def get_location_sensors(
            self, location_name_str):
        """ get_location_sensors()
                Takes the location name as a string.
                Returns the list of adjacent locations to build the ontology with.

                Example:

                dataset_object.get_location_sensors('bedroom') returns ['D001', 'LS006'].
        """
        try:
            return self.dataset_conf['sensors']['locations'][location_name_str]
        except KeyError as e:
            s = "Cannot find sensor list for location with name '%s'" % (
                location_name_str,)
            logger.debug(s)
            return []

    def apply_line_pattern(self, line):
        """ apply_line_pattern
                Takes a line from the data file as argument.
                Returns a dict containing the following structure:
                {
                    'timestamp': '...',
                    'sensor': {
                        'name':"...",
                        'type': TheConvertedInstantiableSensorType,
                        'state': theConvertedSensorState
                    },
                    'activity': {
                        'name': "...",
                        'type': TheConvertedInstantiableActivityType,
                        'state': theConvertedActivityState
                    }
                }

                activity can be None.
                Using regex can be the simplest way to implement this function.
                Make use of the mapping functions defined above.
        """
        extracted = {}
        tokens = self.line_pattern.search(line)

        extracted['timestamp'] = tokens.group(1)
        extracted['sensor'] = {
            'name': '%s%s' % (tokens.group(2), tokens.group(3)),
            'type': self._sensor_type_mapping(tokens.group(2)),
            'state': self.sensor_state_mapping(tokens.group(4).lower())
        }
        extracted['activity'] = None

        if tokens.group(6):
            act_tokens = self.activity_pattern.search(tokens.group(6))

            if act_tokens.group(3):
                act_state = act_tokens.group(3).lower()
            else:
                act_state = None

            extracted['activity'] = {
                'name': act_tokens.group(1),
                'type': self.activity_type_mapping(act_tokens.group(1)),
                'state': self.activity_state_mapping(act_state)
            }

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
        return os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '.data', self.dataset_conf['datapath']))

    @property
    def name(self):
        """ Property: name
                Returns the name of the dataset.
        """
        return self.dataset_name
