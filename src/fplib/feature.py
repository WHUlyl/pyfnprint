import numpy as np

from fplib.minutae import MnType


def _get_core(minutae: np.array):
    return [point for point in minutae if point[2] == MnType.Core][0]


def _extract_polar(minutae: np.array):
    """ Return vector of polar distances to core """
    core = _get_core(minutae)
    if core is None:
        raise Exception('missing core point for polar method')

    features = np.empty()
    for point in minutae:
        i, j, t, a = point if len(point) == 4 else point + (None,)

    return features


def _extract_circular(minutae: np.array,
                      bucketsize: float):
    """ Return vector of features per concentric circle of n*bucketsize """
    core = _get_core(minutae)
    if core is None:
        raise Exception('missing core point for circular method')

    dist = []
    for point in minutae:
        i, j, t, _ = point if len(point) == 4 else point + (None,)
        dist.append(np.linalg.norm(
            np.array((core[0], core[1])) - np.array((i, j))))

    feat = []
    for i in range(0, int(np.max(dist)/bucketsize) + 1):
        feat.append({ MnType.Termination: 0, MnType.Bifurcation: 0 })
    for i in range(0, len(dist)):
        t = minutae[i][2]
        if t == MnType.Termination or t == MnType.Bifurcation:
            feat[int(dist[i]/bucketsize)][t] += 1

    return np.array(feat)


def extract(minutae: np.array,
            method: str=None,
            bucketsize: float=None):
    """
    Extracts feature points from the minutae list

    Arguments:
        minutae    - minutae list consisting of tuples \
            (row, col, type, angle). Can be acquired via minutae() function
        method     - feature vector type, one of ['polar', 'circular']
        bucketsize - distance per bucket for 'circular' method

    Returns tuple (features, method)
    """
    if method == 'polar':
        return (_extract_polar(minutae), method)
    elif method == 'circular':
        if bucketsize is None:
            raise Exception('bucketsize must be provided for circular method')
        return (_extract_circular(minutae, bucketsize), method)
    else:
        raise Exception(method + ' is not supported')
