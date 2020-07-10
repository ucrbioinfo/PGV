from globalVariables import *
from linkNodes import linkNodes
from merge import merge

def getConsensus(nodeOrders, chrmEndCNodes):
    unlink = dict()  ## unlink[node] = [ (left, right), (left, right), ... ] list of tuples
    CnodeOrders = []
    for j in range(len(nodeOrders)):
        nodeOrder = nodeOrders[j]
        CnodeOrder = ["dummy"] ## Cnodes only in the list with dummyHead/Tail
        for i in range(len(nodeOrder)):
            if nodeOrder[i].startswith("C"):
                CnodeOrder.append(nodeOrder[i])
                if nodeOrder[i] in chrmEndCNodes[j]:
                    CnodeOrder.append("dummy")
        CnodeOrder.append("dummy")
        CnodeOrders.append(CnodeOrder[1:-1])
        for i in range(1, len(CnodeOrder)-1): ## instead of range(2, len(CnodeOrder)-2) Aug 21
            node = CnodeOrder[i]
            if node.startswith("C"):
                neighbors = [CnodeOrder[i-1],CnodeOrder[i+1]]
                unlink[node] = unlink[node]+neighbors if node in unlink else neighbors

    linked = linkNodes(unlink)
    consensus = merge(CnodeOrders, linked)
    return consensus