from getTop2 import getTop2


def linkNodes(unlink):
    linked = dict()
    while bool(unlink):
        curNode, neighbors = unlink.popitem()
        ## two most common neighbor nodes without ties
        top2c = getTop2(neighbors)
        top2 = []
        for node in top2c:
            if node in unlink:
                top2.append(node)
        curPath = [curNode]
        extendLeft = False
        extendRight = False
        if len(top2) == 1:
            curPath = [top2[0], curNode]
            extendLeft = True
        elif len(top2) == 2:
            curPath = [top2[0], curNode, top2[1]]
            extendLeft = True
            extendRight = True
        while extendLeft:
            leftNode = curPath[0]
            if leftNode in unlink:
                top2 = getTop2(unlink[leftNode])
                unlink.pop(leftNode)
            else:
                top2 = []
            ## pick the next one to append to the left
            for node in top2:
                if node not in curPath:
                    leftNode = node
            ## could not find the next leftNode
            if leftNode == curPath[0]:
                extendLeft = False
            else:
                ## next leftNode is unlink --> just add it and continue
                if leftNode in unlink:
                    curPath = [leftNode] + curPath
                ## next leftNode is linked --> append the whole path
                elif leftNode in linked:
                    extendPath = linked[leftNode]
                    linked.pop(extendPath[0])
                    if extendPath[-1] in linked:
                        linked.pop(extendPath[-1])
                    if leftNode == extendPath[0]:
                        extendPath.reverse()
                    curPath = extendPath + curPath
                    extendLeft = False
                else: 
                    extendLeft = False ##add May13
        while extendRight:
            rightNode = curPath[-1]
            if rightNode in unlink:
                top2 = getTop2(unlink[rightNode])
                unlink.pop(rightNode)
            else:
                top2 = []
            for node in top2:
                if node not in curPath:
                    rightNode = node
            if rightNode == curPath[-1]:
                extendRight = False
            else:
                if rightNode in unlink:
                    curPath = curPath + [rightNode]
                elif rightNode in linked:
                    extendPath = linked[rightNode]
                    linked.pop(extendPath[0])
                    if extendPath[-1] in linked:
                        linked.pop(extendPath[-1])
                    if rightNode == extendPath[-1]:
                        extendPath.reverse()
                    curPath = curPath + extendPath
                    extendRight = False
                else:
                    extendRight = False ##add May13
        linked[curPath[0]] = curPath
        linked[curPath[-1]] = curPath

    return linked
