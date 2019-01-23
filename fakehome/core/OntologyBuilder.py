import os
from owlready2 import *

import logging
logger = logging.getLogger(__name__)
from tqdm import tqdm

from .BaseOntology import *
from .DatasetObject import DatasetObject


class OntologyBuilder(object):
    """docstring for OntologyBuilder"""

    def __init__(self, dataset):
        super(OntologyBuilder, self).__init__()
        if not isinstance(dataset, DatasetObject):
            s = "The OntologyBuilder must be built from a DatasetObject. \
                Wrong type for 'dataset': %s" % (type(dataset),)
            logger.error(s)
            raise AttributeError(s)

        self.dataset = dataset

        if logger.getEffectiveLevel() < logging.WARNING:
            print("Building ontology from dataset %s..." %
                  (self.dataset.name,))
        else:
            print("Building ontology from dataset %s... " %
                  (self.dataset.name,), end='')

        with open(self.dataset.filepath, 'r') as f:
            self.file_length = len(f.readlines())
            logger.debug(
                "Found %s lines in file %s",
                self.file_length, self.dataset.filepath)

        self.working_ontology = get_ontology(os.path.join(
            self.dataset.filepath, self.dataset.name + ".owl"))

        with self.working_ontology:
            # Create the locations
            self.locations = {
                name: self.dataset.location_type_mapping(name)()
                for name in self.dataset.location_list
            }
            logger.debug("Found locations: %s", self.dataset.location_list)

            # Create a sensor dictionnary
            self.sensors = {}

            for (loc, loc_instance) in tqdm(
                    self.locations.items(), desc="Creating ontology", ascii=True):
                # Create adjacency relationships between locations
                try:
                    for other in self.dataset.get_location_adjacency(loc):
                        other_instance = self.locations[other]
                        loc_instance.is_adjacent_to.append(other_instance)
                        other_instance.is_adjacent_to.append(loc_instance)
                except KeyError as e:
                    logger.warning(
                        'Cannot find other: {}. Continuing.'.format(other))
                logger.debug(
                    "Processed location adjacencies for location %s.", loc)

                # Create sensors and attach them to location
                for sensor in self.dataset.get_location_sensors(loc):
                    # Raise an error if sensor already exist to avoid side
                    # # effects
                    if sensor not in self.sensors.keys():
                        self.sensors[sensor] = \
                            self.dataset.sensor_name_mapping(
                                sensor)(
                                    name=sensor, has_location=loc_instance)
                    else:
                        s = "Sensor %s is in 2 locations..." % (sensor,)
                        logger.error(s)
                        raise AssertionError(s)
                logger.debug("Processed sensor creation for location %s.", loc)

            print("Ok !")
            self.training_slice = None

    def read_data(self, window_size=-1, starting_line=0):
        logger.debug(
            "Reading slice [%s, %s] from dataset %s...", starting_line,
            window_size if window_size != -1 else self.file_length,
            self.dataset.name
        )

        with self.working_ontology:
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

            with open(self.dataset.filepath, 'r') as file:
                if window_size == -1:
                    lines = file.readlines()[starting_line:]
                elif starting_line + window_size > self.file_length:
                    lines = file.readlines()[starting_line:]
                    raise Warning("Trying to read %d lines, but annotated data file contains %d lines." % (
                        starting_line + window_size, self.file_length))
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
                        event = self.dataset.apply_line_pattern(line)

                    except KeyError as e:
                        num_errors += 1
                        logger.debug(
                            "Get KeyError while attempting to read line %s of dataset %s. \
                            Please check your dataset and line pattern.", idx, self.dataset.name)
                        continue

                    # Add a new sensor measure to the sensor event list
                    try:
                        sensor_events.append(
                            Measure(
                                is_measured_by=self.sensors[
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
                            activity_state.python_name, event['timestamp'])

                        activity_events.append(activity)
                print("Ok ! Read %s lines out of %s..." %
                      (num_lines - num_errors, num_lines))

        self.training_slice['start'] = starting_line
        self.training_slice['stop'] = starting_line + window_size
        self.training_slice['sensor_events'] = sensor_events
        self.training_slice['activity_events'] = activity_events

        return self.training_slice
