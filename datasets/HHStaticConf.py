HH101_STATIC_CONF = {
    'locations': [
        'kitchen',
        'living_room',
        'entrance',
        'bedroom',
        'bathroom'
    ],
    'locations_adjacency': {
        'living_room': ['kitchen', 'entrance'],
        'entrance': ['bedroom', 'bathroom']
    },
    'sensors_locations': {
        'D001': 'entrance',
        'D002': 'entrance',
        'T102': 'entrance',
        'T103': 'bathroom',
        'T101': 'entrance',
        'MA016': 'kitchen',
        'D003': 'bathroom',
        'M009': 'bedroom',
        'LS010': 'entrance',
        'M010': 'entrance',
        'LS011': 'bedroom',
        'M007': 'kitchen',
        'LS008': 'living_room',
        'M008': 'living_room',
        'LS009': 'bedroom',
        'M011': 'bedroom',
        'LS012': 'bedroom',
        'LS001': 'entrance',
        'LS002': 'kitchen',
        'M001': 'entrance',
        'LS016': 'kitchen',
        'T105': 'entrance',
        'T104': 'entrance',
        'LS003': 'kitchen',
        'M002': 'kitchen',
        'LS004': 'living_room',
        'M003': 'kitchen',
        'LS005': 'living_room',
        'M004': 'kitchen',
        'LS006': 'kitchen',
        'M005': 'living_room',
        'LS007': 'kitchen',
        'MA013': 'living_room',
        'LS013': 'living_room',
        'M012': 'kitchen',
        'MA015': 'bathroom',
        'LS015': 'bathroom',
        'MA014': 'bedroom',
        'LS014': 'bedroom',
        'M006': 'kitchen',
    }
}

datasets_confs = {
    'hh101': HH101_STATIC_CONF
}
