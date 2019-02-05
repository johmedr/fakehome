import networkx as nx
import numpy as np

from scipy.linalg import fractional_matrix_power

import logging
logger = logging.getLogger(__name__)

from .FakeHomeOntology import FakeHomeOntology


def adjacency_from_ontology(fakehomeontology):
    if not isinstance(fakehomeontology, FakeHomeOntology):
        raise AttributeError()

    nsensors = len(fakehomeontology.sensors)
    nlocations = len(fakehomeontology.locations)
    N = nsensors + nlocations

    # Adjacency is an NxN matrix. The nsensors first elements ([0, nsensors - 1]) refer to
    # sensors, and the nlocations remaining elements ([nsensors, N -
    # 1]) refer to locations
    adjacency = np.zeros((N, N), dtype=np.float)

    # Sensors are stored in an (unordererd) dictionnary. We have to give
    # a fixed ordering here
    sensors_list = [fakehomeontology.sensors[k]
                    for k in sorted(fakehomeontology.sensors.keys())]
    # Same for the locations
    locations_list = [fakehomeontology.locations[k]
                      for k in sorted(fakehomeontology.locations.keys())]

    for i, sensor in enumerate(sensors_list):
        j = locations_list.index(sensor.has_location) + nsensors
        adjacency[i, j] = 1.
        adjacency[j, i] = 1.

    for idx, location in enumerate(locations_list):
        i = idx + nsensors
        for other_location in location.is_adjacent_to:
            j = locations_list.index(other_location) + nsensors
            adjacency[i, j] = 1.

    return adjacency, sensors_list, locations_list


def normalize_adjacency(A, symmetric=True):
    """ normalize_adjacency
        Computes the normalized adjacency matrix, either using symmetric 
        or asymmetric normalization. 
        Please note that the Moore-Penrose pseudo-inverse is used instead of 
        a straight inverse.  
    """
    D = np.diag(np.sum(A, axis=0))
    D_1 = np.linalg.pinv(D)

    if symmetric:
        D_12 = fractional_matrix_power(D_1, 0.5)
        A_norm = D_12.dot(A).dot(D_12)
    else:
        A_norm = D_1.dot(A)

    return A_norm


class FakeHomeGraph(nx.Graph):

    def __init__(self, ontology=None, **attr):
        if not isinstance(ontology, FakeHomeOntology):
            raise AttributeError(
                "Fake home graph must be built from a FakfHomeOntology object")

        self._ontology = ontology

        self._adjacency, self._sensors_list, self._locations_list = adjacency_from_ontology(
            self._ontology)

        self._nsensors = len(self._sensors_list)
        self._nlocations = len(self._locations_list)
        self._N = self._adjacency.shape[0]

        # A ordering for the nodes' features is obtained here
        self._features_list = list(set(type(e)
                                       for e in self._sensors_list + self._locations_list))
        self._F = len(self._features_list)

        self._activities_list = list(set(self._ontology._dataset.activity_type_mapping(a)
                                         for a in self._ontology.activities))
        self._nactivities = len(self._activities_list)

        super(FakeHomeGraph, self).__init__(self._adjacency, **attr)

        for idx, sensor in enumerate(self._sensors_list):
            self.node[idx]['name'] = sensor.name
            self.node[idx]['instance'] = sensor

        for idx, loc in enumerate(self._locations_list):
            self.node[idx + self._nsensors]['name'] = loc.name
            self.node[
                idx + self._nsensors]['instance'] = loc

        self._normalized_adjacency = None
        self._laplacian = None

    def draw(self, pos=None):
        if pos is None:
            try:
                pos = nx.nx_agraph.graphviz_layout(self)
            except ImportError as e:
                logger.warning(e)
                pos = nx.spring_layout(self, k=(1. / self._N) * 10)

        labels = {i: self.node[i]['name'].replace(
            "location", "").replace('1', '') for i in self.nodes()}
        node_color = ['lightseagreen' if i <
                      self._nsensors else 'indianred' for i in self.nodes()]
        charsize = 300
        node_size = [len(v) * charsize for v in labels.values()]

        return nx.draw(
            self,
            pos=pos,
            node_size=node_size,
            node_color=node_color,
            with_labels=True,
            labels=labels,
            font_size=10
        )

    def draw3d(self, bgcolor=(1, 1, 1),
               node_size=10.,
               edge_color=(0.8, 0.8, 0.8), edge_size=1.,
               text_size=0.075, text_color=(0, 0, 0)):
        try:
            from mayavi import mlab
            from matplotlib.colors import to_rgba

        except ImportError as e:
            logger.error("Cannot use draw3d without mayavi.")
            raise e

        graph_pos = nx.nx_agraph.graphviz_layout(self)

        # numpy array of x,y,z positions in sorted node order
        xyz = np.array([graph_pos[v] + (0,) for v in sorted(self)])

        # Clear figure
        mlab.figure(1, bgcolor=bgcolor)
        mlab.clf()

        # Setup 2 different layers, for sensors and locations
        xyz[:self._nsensors, 2] = 0.
        xyz[self._nsensors:, 2] = 60.

        # Create points
        pts = mlab.points3d(xyz[:, 0], xyz[:, 1], xyz[:, 2], range(self._N),
                            scale_factor=node_size,
                            scale_mode='none',
                            resolution=20)

        # Setup a lookup table for colors
        node_color = [to_rgba('lightseagreen') if i <
                      self._nsensors else to_rgba('indianred') for i in self.nodes()]
        node_color = [[int(c * 255) for c in t] for t in node_color]

        pts.module_manager.scalar_lut_manager.lut._vtk_obj.SetTableRange(
            0, 255)
        pts.module_manager.scalar_lut_manager.lut.table = node_color

        # Add labels with different size for locations and sensors names
        labels = {i: self.node[i]['name'].replace(
            "location", "") for i in self.nodes()}

        for i, (x, y, z) in enumerate(xyz):
            if i < self._nsensors:
                mlab.text(x, y, labels[i], z=z,
                          width=text_size, name=labels[i], color=text_color)
            else:
                mlab.text(x, y, labels[i], z=z,
                          width=text_size * 4, name=labels[i], color=text_color)

        # Add edges
        pts.mlab_source.dataset.lines = np.array(self.edges())
        tube = mlab.pipeline.tube(pts, tube_radius=edge_size)
        mlab.pipeline.surface(tube, color=edge_color)

        # Visualize with mayavi
        mlab.show()

    def events_to_nodes_features(self, events):
        if not isinstance(events, dict) or not 'sensor_events' in events.keys():
            raise AttributeError()

        measures = events["sensor_events"]
        X = np.zeros((self._N, self._F, len(measures)), dtype=np.float)

        # One-hot coding of the location
        self._locations_features = np.zeros(
            (self._nlocations, self._F), dtype=np.float)
        for i, loc in enumerate(self._locations_list):
            j = self._features_list.index(type(loc))
            self._locations_features[i, j] = 1.0

        # The locations will remain unchanged during the process
        X[self._nsensors:, :, 0] = self._locations_features

        timevec = []

        for idx, measure in enumerate(measures):
            # Ensure temporal consistence
            if idx > 0:
                X[:, :, idx] = X[:, :, idx - 1]

            # Assign sensor value
            sensor = measure.is_measured_by
            feature = type(sensor)
            i = self._sensors_list.index(sensor)
            j = self._features_list.index(feature)
            X[i, j, idx] = measure.value

            timevec.append(measure.timestamp)

        return X, timevec

    def events_to_activity_features(self, events):
        if not isinstance(events, dict) or not 'sensor_events' in events.keys():
            raise AttributeError()

        measures = events["sensor_events"]
        Y = np.zeros(len(measures), dtype=np.long)

        print(self._ontology.activities)

        for idx, measure in enumerate(measures):
            activity_num = 0

            if measure.occurs_with_activity is not None:
                activity = measure.occurs_with_activity
                if activity.begins_at is not None or activity.timestamp is not None:
                    activity_num = self._activities_list.index(
                        type(activity)) + 1
                # Implicit :
                # elif activity.ends_at is not None:
                #     activity_num = 0
            else:
                if idx > 0:
                    activity_num = Y[idx - 1]

            Y[idx] = activity_num

        return Y

    def read_data(self, window_size=-1, starting_line=0, return_labels=False):
        events = self._ontology.read_data(window_size, starting_line)
        X, T = self.events_to_nodes_features(events)
        if return_labels:
            return T, X, self.events_to_activity_features(events)
        else:
            return X

    @property
    def N(self):
        return self._N

    @property
    def F(self):
        return self._F

    @property
    def symnorm_adjacency(self):
        if self._normalized_adjacency is None:
            self._normalized_adjacency = normalize_adjacency(
                self._adjacency, symmetric=True)
        return self._normalized_adjacency

    @property
    def normalized_laplacian(self):
        if self._laplacian is None:
            self._laplacian = np.eye(self._N) - self.symnorm_adjacency
        return self._laplacian
