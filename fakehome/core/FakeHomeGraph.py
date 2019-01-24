import networkx as nx
import numpy as np

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

        super(FakeHomeGraph, self).__init__(self._adjacency, **attr)

        for idx, sensor in enumerate(self._sensors_list):
            self.node[idx]['name'] = sensor.name
            self.node[idx]['instance'] = sensor

        for idx, loc in enumerate(self._locations_list):
            self.node[idx + self._nsensors]['name'] = loc.name
            self.node[
                idx + self._nsensors]['instance'] = loc

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

        # return nx.draw(self, with_labels=True, labels=labeldict)
