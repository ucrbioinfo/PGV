from . import get_top2


def link_nodes(unlink):
    linked = dict()
    while bool(unlink):
        cur_node, neighbors = unlink.popitem()
        ## two most common neighbor nodes without ties
        top2c = get_top2.get_top2(neighbors)
        top2 = []
        for node in top2c:
            if node in unlink:
                top2.append(node)
        cur_path = [cur_node]
        extend_left = False
        extend_right = False
        if len(top2) == 1:
            cur_path = [top2[0], cur_node]
            extend_left = True
        elif len(top2) == 2:
            cur_path = [top2[0], cur_node, top2[1]]
            extend_left = True
            extend_right = True
        while extend_left:
            left_node = cur_path[0]
            if left_node in unlink:
                top2 = get_top2.get_top2(unlink[left_node])
                unlink.pop(left_node)
            else:
                top2 = []
            ## pick the next one to append to the left
            for node in top2:
                if node not in cur_path:
                    left_node = node
            ## could not find the next leftNode
            if left_node == cur_path[0]:
                extend_left = False
            else:
                ## next leftNode is unlink --> just add it and continue
                if left_node in unlink:
                    cur_path = [left_node] + cur_path
                ## next leftNode is linked --> append the whole path
                elif left_node in linked:
                    extendPath = linked[left_node]
                    linked.pop(extendPath[0])
                    if extendPath[-1] in linked:
                        linked.pop(extendPath[-1])
                    if left_node == extendPath[0]:
                        extendPath.reverse()
                    cur_path = extendPath + cur_path
                    extend_left = False
                else:
                    extend_left = False ##add May13
        while extend_right:
            right_node = cur_path[-1]
            if right_node in unlink:
                top2 = get_top2.get_top2(unlink[right_node])
                unlink.pop(right_node)
            else:
                top2 = []
            for node in top2:
                if node not in cur_path:
                    right_node = node
            if right_node == cur_path[-1]:
                extend_right = False
            else:
                if right_node in unlink:
                    cur_path = cur_path + [right_node]
                elif right_node in linked:
                    extendPath = linked[right_node]
                    linked.pop(extendPath[0])
                    if extendPath[-1] in linked:
                        linked.pop(extendPath[-1])
                    if right_node == extendPath[-1]:
                        extendPath.reverse()
                    cur_path = cur_path + extendPath
                    extend_right = False
                else:
                    extend_right = False ##add May13
        linked[cur_path[0]] = cur_path
        linked[cur_path[-1]] = cur_path

    return linked
