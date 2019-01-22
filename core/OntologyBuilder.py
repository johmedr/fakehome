import os
from owlready2 import *

import logging
logger = logging.getLogger(__name__)

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

        with open(self.dataset.filepath, 'r') as f:
            self.file_length = len(f.readlines())

        self.working_ontology = get_ontology(os.path.join(
            self.dataset.filepath, self.dataset.name + ".owl"))

        with self.working_ontology:
            # Create the locations
            self.locations = {
                name: self.dataset.location_type_mapping(name)()
                for name in self.dataset.location_list
            }

            # Create a sensor dictionnary
            self.sensors = {}

            for (loc, loc_instance) in self.locations.items():
                # Create adjacency relationships between locations
                try:
                    for other in self.dataset.get_location_adjacency(loc):
                        other_instance = self.locations[other]
                        loc_instance.is_adjacent_to.append(other_instance)
                        other_instance.is_adjacent_to.append(loc_instance)
                except KeyError as e:
                    logger.warning(
                        'Cannot find other: {}. Continuing.'.format(other))

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
