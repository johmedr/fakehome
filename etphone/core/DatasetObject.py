import logging
logger = logging.getLogger(__name__)


class DatasetObject(object):
    """ DatasetObject """

    def __init__(self, *args, **kwargs):
        logger.debug(
            "DatasetObject's __init__() method was called. There is no need to call this method in subclasses.")

    @staticmethod
    def _not_implemented_error():
        e = NotImplementedError(
            "Subclasses of DatasetObject must override this method.")
        logger.error(e)
        raise e

    def sensor_name_mapping(
            self, sensor_name_str):
        """ sensor_type_mapping()
                Takes the sensor name as a string extracted from the data file.
                Returns the associated type to build the ontology with.

                If the sensor name contains information about its type, using regex and lookup table can be the simplest way to implement this function.

                Example:

                dataset_object.sensor_type_mapping('LS') returns LightSensorType.
        """
        DatasetObject._not_implemented_error()

    def sensor_state_mapping(
            self, sensor_state_str):
        """ sensor_state_mapping()
                Takes the sensor state as a string extracted from the data file.
                Returns the desired value that will be used to create the Measure instance. That type must be convertible to a float.

                Example:

                dataset_object.sensor_state_mapping('ON') returns 1
        """
        DatasetObject._not_implemented_error()

    def activity_type_mapping(
            self, activity_type_str):
        """ activity_type_mapping()
                Takes the activity type as a string extracted from the data file.
                Returns the associated type to build the ontology with.

                Example:

                dataset_object.activity_type_mapping('cooking') returns CookingActivity.
        """
        DatasetObject._not_implemented_error()

    def activity_state_mapping(
            self, activity_state_str):
        """ activity_state_mapping()
                Takes the activity state as a string extracted from the data file.
                Returns the type of relation to build for this state.
                Please note that the relation type must take a timestamp as an argument.

                Example:

                dataset_object.activity_state_mapping('begins') returns beginsAt
        """
        DatasetObject._not_implemented_error()

    def location_type_mapping(
            self, location_name_str):
        """ location_type_mapping()
                Takes the location name as a string.
                Returns the associated type to build the ontology with.

                If the location name contains information about its type, using regex and lookup table can be the simplest way to implement this function.

                Example:

                dataset_object.location_type_mapping('bedroom') returns BedroomLocation.
        """
        DatasetObject._not_implemented_error()

    def get_location_adjacency(
            self, get_location_adjacency):
        """ location_adjacency_mapping()
                Takes the location name as a string.
                Returns the list of adjacent locations to build the ontology with.

                Example:

                dataset_object.get_location_adjacency('bedroom') returns ['living_room', 'bathroom1'].
        """
        DatasetObject._not_implemented_error()

    def get_location_sensors(
            self, location_name_str):
        """ get_location_sensors()
                Takes the location name as a string.
                Returns the list of adjacent locations to build the ontology with.

                Example:

                dataset_object.get_location_sensors('bedroom') returns ['D001', 'LS006'].
        """

    def apply_line_pattern(self, line):
        """ apply_line_pattern
                Takes a line from the data file as argument. 
                Returns a dict containing the following structure:
                {
                    'timestamp': '...',
                    'sensor': {
                        'name':"...", 
                        'type': TheConvertedInstantiableSensorType,
                        'value': theConvertedValue
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
        DatasetObject._not_implemented_error()

    @property
    def sensor_list(self):
        """ Property: sensor_list
                Returns the list of sensors used in the dataset. 
        """
        DatasetObject._not_implemented_error()

    @property
    def activity_list(self):
        """ Property: activity_list
                Returns the list of activities used in the dataset. 
        """
        DatasetObject._not_implemented_error()

    @property
    def location_list(self):
        """ Property: location_list
                Returns the list of locations used in the dataset. 
        """
        DatasetObject._not_implemented_error()

    @property
    def filepath(self):
        """ Property: filepath
                Returns the absolute path to the data file. 
        """
        DatasetObject._not_implemented_error()

    @property
    def name(self):
        """ Property: name
                Returns the name of the dataset.
        """
        DatasetObject._not_implemented_error()
