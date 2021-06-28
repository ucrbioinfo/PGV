from . import link_nodes
from . import merge


def get_consensus(node_orders, chrm_end_c_nodes, input_genomes, aln_score_thr):
    unlink = dict()  ## unlink[node] = [ (left, right), (left, right), ... ] list of tuples
    cnode_orders = []
    for j in range(len(node_orders)):
        node_order = node_orders[j]
        c_node_order = ["dummy"] ## Cnodes only in the list with dummyHead/Tail
        for i in range(len(node_order)):
            if node_order[i].startswith("C"):
                c_node_order.append(node_order[i])
                if node_order[i] in chrm_end_c_nodes[j]:
                    c_node_order.append("dummy")
        c_node_order.append("dummy")
        cnode_orders.append(c_node_order[1:-1])
        for i in range(1, len(c_node_order)-1): ## instead of range(2, len(CnodeOrder)-2) Aug 21
            node = c_node_order[i]
            if node.startswith("C"):
                neighbors = [c_node_order[i-1], c_node_order[i+1]]
                unlink[node] = unlink[node]+neighbors if node in unlink else neighbors

    linked = link_nodes.link_nodes(unlink)
    consensus = merge.merge(cnode_orders, linked, input_genomes, aln_score_thr)
    return consensus