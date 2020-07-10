from globalVariables import *
import sys
import re
import numpy
from processXMFA import processXMFA
from getConsensus import getConsensus
from getBED import getBED
from plot import plot

nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes = processXMFA()

consensus = getConsensus(nodeOrders, chrmEndCNodes)

getBED(consensus, nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes)

plot()
