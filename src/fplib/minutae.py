from enum import Enum
from itertools import combinations
from math import tan

import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances


from fplib.preprocess import _orientblk_angle


verbose = False


class Type(Enum):
    Core = 1,
    Bifurcation = 2,
    Termination = 3


def minutae(sklt: np.array,
            orient: np.array=None,
            ridge_value: bool=1,
            remove_invalid: bool=1):
    """
    Extract minutae points from the skeleton image

    Arguments:
        sklt           - skeleton image
        orient         - orientation matrix. Can be acquired via the \
orientation() function
        ridge_value    - value of ridge pixels
        remove_invalid - whether to remove invalid minutae

    Return list of tuples with minutae coordinates (row, col, type, angle)
    """
    idx = [(0,0), (1,0), (2,0), (2,1), (2,2), (1,2), (0,2), (0,1), (0,0)]
    points = []
    for i in range(1, sklt.shape[0] - 1):
        for j in range(1, sklt.shape[1] - 1):
            if not sklt[i][j] == ridge_value:
                continue

            blk = sklt[i - 1:i + 2, j - 1:j + 2]

            # pfunc value is equal to the number of ridges that come into block
            psums = [blk[k1] * (1 - blk[k2]) for k1, k2 in zip(idx, idx[1:])]
            pfunc = np.sum(psums)

            angle = None
            if pfunc == 1:
                if orient is not None:
                    angle = _orientblk_angle(orient, (i, j), 3)
                points.append((i, j, Type.Termination, angle))
            elif pfunc > 2:
                if orient is not None:
                    angle = _orientblk_angle(orient, (i, j), 3)
                points.append((i, j, Type.Bifurcation, angle))

            if verbose:
                # PLOT: image block 3x3
                plt.figure()
                plt.imshow(blk, cmap='gray')
                plt.text(-0.5, -0.6, 'pfunc = ' + str(pfunc), color='black')
                plt.show()

    # Remove border terminations
    if remove_invalid:
        points = _remove_border_points(sklt, points, ridge_value)
    return np.array(points)


def _remove_border_points(sklt: np.array,
                          minutiae: tuple,
                          ridge_value: bool=1):
    """ Remove border minutae points """
    result = []
    for point in minutiae:
        i, j, _, _ = point
        # Count as a border if there is a direction with only ridge 0 pixels
        if (ridge_value in sklt[i, :j]) and\
           (ridge_value in sklt[:i, j]) and\
           (ridge_value in sklt[i, j + 1:]) and\
           (ridge_value in sklt[i + 1:, j]):
           result.append(point)
    return result
