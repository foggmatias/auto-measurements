import numpy
import matplotlib.pyplot as plt

def reject_outliers(data, m=2.):
    data=numpy.asarray(data,dtype=numpy.float64)
    d = numpy.abs(data - numpy.median(data))
    mdev = numpy.median(d)
    s = d / (mdev if mdev else 1.)
    return data[s < m].tolist()


def takeSecond(elem): return elem[1]
def takeFirst(elem): return elem[0]
                                
