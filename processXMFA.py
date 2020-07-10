import sys
import re
import numpy

from globalVariables import *
from getChrmEnds import getChrmEnds

#def processXMFA(XMFAFile, numOfGenomes):
def processXMFA():
    chrmEnds = getChrmEnds()

    INPUT = open(XMFAFile, "r")

    SEQ_DELIMITER = ">"
    BLOCK_DELIMITER = "="
    REGX_PATTERN = re.compile(">\\s+(\\d+):(\\d+)-(\\d+)\\s+[+-]\\s+(\\S+)")


    #### store XMFA info
    blockSeqs = dict()
    allBlocks = []

    allBlocksDict = dict()
    commonCount = 0
    partialCount = 0
    uniqCount = 0

    for line in INPUT:
        if (line.startswith(SEQ_DELIMITER)):
            seq = REGX_PATTERN.match(line)
            if (seq.group(3) != "0"):
                blockSeqs[int(seq.group(1))-1] = (int(seq.group(2)), int(seq.group(3))) ## gID orignially [1,n], now with -1 [0,n-1]
        elif (line.startswith(BLOCK_DELIMITER)):
            allBlocks.append(dict(blockSeqs))
            if (len(blockSeqs) == 1):
                allBlocksDict["U"+str(uniqCount)] = dict(blockSeqs)
                uniqCount += 1
            elif (len(blockSeqs) == numOfGenomes):
                allBlocksDict["C"+str(commonCount)] = dict(blockSeqs)
                commonCount += 1
            else:
                allBlocksDict["D"+str(partialCount)] = dict(blockSeqs)
                partialCount += 1
            blockSeqs.clear()


    #### get node info
    allStarts = [ [] for x in range(numOfGenomes)]  # Store startLocation of all nodes. Sort and print in order
    start2node = [ {} for x in range(numOfGenomes)]
    nodeLengths = dict()

    for node in allBlocksDict:
        nodeInfo = allBlocksDict[node]
        nodeLength = []
        for gID in range(numOfGenomes):
            length = 0 ## node does not exist in gID
            if gID in nodeInfo: ## get start location
                start = nodeInfo[gID][0]
                allStarts[gID].append(start)
                start2node[gID][start] = node
                length = nodeInfo[gID][1] - nodeInfo[gID][0] +1
            nodeLength.append(length)
        #remove 0s for unexisting block on genome(s) for D/U
        tmpLength = [x for x in nodeLength if x != 0]
        nodeLength += [numpy.average(tmpLength), numpy.std(tmpLength)]
        nodeLengths[node] = nodeLength


    #### get node orders
    nodeOrders = []
    chrmEndNodes = []
    chrmEndCNodes = []
    for gID in range(numOfGenomes):
        nodeOrder = []
        allStarts[gID].sort()
        startOrder = allStarts[gID]

        prevNode = None
        prevCNode = None
        currChrmI = 0
        chrmEndNode = []
        chrmEndCNode = []

        for start in startOrder:
            currNode = start2node[gID][start]
            nodeOrder.append(currNode)
            if start > chrmEnds[gID][currChrmI]:
                chrmEndNode.append(prevNode)
                chrmEndCNode.append(prevCNode)
                currChrmI += 1
            prevNode = currNode
            if currNode.startswith("C"):
                prevCNode = currNode

        chrmEndNode.append(prevNode)
        chrmEndCNode.append(prevCNode)
        nodeOrders.append(nodeOrder)
        chrmEndNodes.append(chrmEndNode)
        chrmEndCNodes.append(chrmEndCNode)

    return (nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes)
