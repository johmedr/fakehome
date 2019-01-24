import os
from owlready2 import *
import numpy as np

import logging
logger = logging.getLogger(__name__)
from tqdm import tqdm

from .BaseOntology import *
from .DatasetObject import DatasetObject


class FakeHomeOntology(object):
    """docstring for FakeHomeOntology"""

    def __init__(self, dataset):
        super(FakeHomeOntology, self).__init__()
        if not isinstance(dataset, DatasetObject):
            s = "The FakeHomeOntology must be built from a DatasetObject. \
                Wrong type for 'dataset': %s" % (type(dataset),)
            logger.error(s)
            raise AttributeError(s)

        self._dataset = dataset

        if logger.getEffectiveLevel() < logging.WARNING:
            print("Building ontology from dataset %s..." %
                  (self._dataset.name,))
        else:
            print("Building ontology from dataset %s... " %
                  (self._dataset.name,), end='')

        with open(self._dataset.filepath, 'r') as f:
            self._file_length = len(f.readlines())
            logger.debug(
                "Found %s lines in file %s",
                self._file_length, self._dataset.filepath)

        self._working_ontology = get_ontology(os.path.join(
            self._dataset.filepath, self._dataset.name + ".owl"))

        with self._working_ontology:
            # Create the locations
            self._locations = {
                name: self._dataset.location_type_mapping(name)()
                for name in self._dataset.location_list
            }
            logger.debug("Found locations: %s", self._dataset.location_list)

            # Create a sensor dictionnary
            self._sensors = {}

            for (loc, loc_instance) in tqdm(
                    self._locations.items(), desc="Creating ontology", ascii=True):
                # Create adjacency relationships between locations
                try:
                    for other in self._dataset.get_location_adjacency(loc):
                        other_instance = self._locations[other]
                        loc_instance.is_adjacent_to.append(other_instance)
                        other_instance.is_adjacent_to.append(loc_instance)
                except KeyError as e:
                    logger.warning(
                        'Cannot find other: {}. Continuing.'.format(other))
                logger.debug(
                    "Processed location adjacencies for location %s.", loc)

                # Create sensors and attach them to location
                for sensor in self._dataset.get_location_sensors(loc):
                    # Raise an error if sensor already exist to avoid side
                    # # effects
                    if sensor not in self._sensors.keys():
                        self._sensors[sensor] = \
                            self._dataset.sensor_name_mapping(
                                sensor)(
                                    name=sensor, has_location=loc_instance)
                    else:
                        s = "Sensor %s is in 2 locations..." % (sensor,)
                        logger.error(s)
                        raise AssertionError(s)
                logger.debug("Processed sensor creation for location %s.", loc)

            self.training_slice = None
            self._adjacency_matrix = None

            print("Ok !")

    def read_data(self, window_size=-1, starting_line=0):
        logger.debug(
            "Reading slice [%s, %s] from dataset %s...", starting_line,
            window_size if window_size != -1 else self._file_length,
            self._dataset.name
        )

        with self._working_ontology:
            if self.training_slice is not None:
                # TODO: What if window size == -1. Improve the mechanism
                if starting_line == self.training_slice['start'] and starting_line + window_size == self.training_slice['stop']:
                    logger.debug("Returning the stored events slice.")
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

            with open(self._dataset.filepath, 'r') as file:
                if window_size == -1:
                    lines = file.readlines()[starting_line:]
                elif starting_line + window_size > self._file_length:
                    lines = file.readlines()[starting_line:]
                    raise Warning("Trying to read %d lines, but annotated data file contains %d lines." % (
                        starting_line + window_size, self._file_length))
                else:
                    lines = file.readlines()[
                        starting_line:starting_line + window_size]

                num_lines = len(lines)
                num_errors = 0

                for idx, line in tqdm(
                    enumerate(lines),
                    desc="Retrieving data",
                    total=num_lines,
                    ascii=True,
                    unit='lines',
                    dynamic_ncols=True
                ):
                    try:
                        event = self._dataset.apply_line_pattern(line)

                    except (KeyError, AttributeError) as e:
                        num_errors += 1
                        logger.debug(
                            "Get KeyError while attempting to read line %s of dataset %s. \
                            Please check your dataset and line pattern.", idx, self._dataset.name)
                        continue

                    # Add a new sensor measure to the sensor event list
                    try:
                        sensor_events.append(
                            Measure(
                                is_measured_by=self._sensors[
                                    event['sensor']['name']],
                                value=event['sensor']['state'],
                                timestamp=event['timestamp']
                            )
                        )

                    except KeyError as e:
                        num_errors += 1
                        logger.debug("Sensor %s is not part of the dataset registered sensors... Skipping...",
                                     event['sensor']['name'])
                        continue

                    if event['activity'] is not None:
                        # Instantiate a new activity
                        activity = event['activity']['type']()
                        # Assign the timestamp to the data property
                        # corresponding to the event, e.g. beginsAt
                        activity.__setattr__(
                            event['activity']['state'].python_name, event['timestamp'])

                        activity_events.append(activity)
                print("Ok ! Read %s lines out of %s..." %
                      (num_lines - num_errors, num_lines))

        self.training_slice['start'] = starting_line
        self.training_slice['stop'] = starting_line + window_size
        self.training_slice['sensor_events'] = sensor_events
        self.training_slice['activity_events'] = activity_events

        return self.training_slice

    def _build_adjacency_matrix(self):
        nsensors = len(self._sensors)
        nlocations = len(self._locations)
        N = nsensors + nlocations

        # Adjacency is an NxN matrix. The nsensors first elements ([0, nsensors - 1]) refer to
        # sensors, and the nlocations remaining elements ([nsensors, N -
        # 1]) refer to locations
        adjacency = np.zeros((N, N), dtype=np.float)

        # Sensors are stored in an (unordererd) dictionnary. We have to give
        # a fixed ordering here
        sensors_list = [self._sensors[k]
                        for k in sorted(self._sensors.keys())]
        # Same for the locations
        locations_list = [self._locations[k]
                          for k in sorted(self._locations.keys())]

        for i, sensor in enumerate(sensors_list):
            j = locations_list.index(sensor.has_location) + nsensors
            adjacency[i, j] = 1.
            adjacency[j, i] = 1.

        for i, location in enumerate(locations_list):
            i += nsensors
            for other_location in location.is_adjacent_to:
                j = locations_list.index(other_location) + nsensors
                adjacency[i, j] = 1.

        self._adjacency_matrix = adjacency

    @property
    def adjacency_matrix(self):
        if self._adjacency_matrix is None:
            self._build_adjacency_matrix()
        return self._adjacency_matrix

    @property
    def sensors(self):
        return self._sensors

    @property
    def locations(self):
        return self._locations

    @property
    def working_ontology(self):
        return self._working_ontology
