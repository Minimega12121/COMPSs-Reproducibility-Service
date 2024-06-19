from pycompss.api.parameter import *
from pycompss.api.api import compss_barrier
from dislib.cluster import KMeans

import dislib as ds
import sys, time
import numpy as np

if __name__ == '__main__':
    gpus = sys.argv[1]
    cache = sys.argv[2]
    blocksize = int(sys.argv[3])
    k = int(sys.argv[4])
    shape_0 = int(sys.argv[5])
    shape_1 = int(sys.argv[6])

    x = ds.random_array((shape_0, shape_1), (blocksize, shape_1), dtype=np.float32)

    kmeans = KMeans(n_clusters=k, max_iter=5)
    kmeans.fit(x)