from globalVariables import *
import sys
import re
import numpy
from processXMFA import processXMFA
from getConsensus import getConsensus
from getBED import getBED
from plot import plot

nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes = processXMFA()
print("Finished processing multiple sequence alignments")

consensus = getConsensus(nodeOrders, chrmEndCNodes)
print("Built consensus sucessfully")

getBED(consensus, nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes)
print("Generated output BED files. Please visit pgv.cs.ucr.edu to view these.")

plot()
print("Generated dotplots between each assembly and consensus sequence")
