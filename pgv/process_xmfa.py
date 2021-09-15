import sys
import re
import numpy

from . import get_chrm_ends


def process_xmfa(input_genomes, xmfa_file, num_of_chrms):
    chrm_ends = get_chrm_ends.get_chrm_ends(input_genomes, num_of_chrms)

    input_file = open(xmfa_file, "r")

    seq_delimiter = ">"
    block_delimiter = "="
    regx_pattern = re.compile(">\\s+(\\d+):(\\d+)-(\\d+)\\s+([+-])\\s+\\S+")


    #### store XMFA info
    block_seqs = dict()
    all_blocks = []

    all_blocks_dict = dict()
    common_count = 0
    partial_count = 0
    uniq_count = 0

    for line in input_file:
        if line.startswith(seq_delimiter):
            seq = regx_pattern.match(line)
            if seq.group(3) != "0":
                block_seqs[int(seq.group(1))-1] = (int(seq.group(2)), int(seq.group(3)), seq.group(4)) ## gID orignially [1,n], now with -1 [0,n-1]
        elif line.startswith(block_delimiter):
            all_blocks.append(dict(block_seqs))
            if len(block_seqs) == 1:
                all_blocks_dict["U"+str(uniq_count)] = dict(block_seqs)
                uniq_count += 1
            elif len(block_seqs) == len(input_genomes):
                all_blocks_dict["C"+str(common_count)] = dict(block_seqs)
                common_count += 1
            else:
                all_blocks_dict["D"+str(partial_count)] = dict(block_seqs)
                partial_count += 1
            block_seqs.clear()


    #### get node info
    all_starts = [[] for x in range(len(input_genomes))]  # Store startLocation of all nodes. Sort and print in order
    start2node = [{} for x in range(len(input_genomes))]
    node_lengths = dict()

    for node in all_blocks_dict:
        node_info = all_blocks_dict[node]
        node_length = []
        for gID in range(len(input_genomes)):
            length = 0 ## node does not exist in gID
            direction = "+"
            if gID in node_info: ## get start location
                start = node_info[gID][0]
                all_starts[gID].append(start)
                start2node[gID][start] = node
                length = node_info[gID][1] - node_info[gID][0] +1
                direction = node_info[gID][2]
            node_length.append((length, direction))
        #remove 0s for unexisting block on genome(s) for D/U
        tmp_length = [x[0] for x in node_length if x[0] != 0]
        node_length += [(numpy.average(tmp_length),), (numpy.std(tmp_length),)]
        node_lengths[node] = node_length


    #### get node orders
    node_orders = []
    chrm_end_nodes = []
    chrm_end_c_nodes = []
    for gID in range(len(input_genomes)):
        node_order = []
        all_starts[gID].sort()
        start_order = all_starts[gID]

        prev_node = None
        prev_c_node = None
        curr_chrm_i = 0
        chrm_end_node = []
        chrm_end_c_node = []

        for start in start_order:
            curr_node = start2node[gID][start]
            node_order.append(curr_node)
            if start > chrm_ends[gID][curr_chrm_i] and curr_chrm_i < len(chrm_ends[gID]) -1:
                chrm_end_node.append(prev_node)
                chrm_end_c_node.append(prev_c_node)
                curr_chrm_i += 1
            prev_node = curr_node
            if curr_node.startswith("C"):
                prev_c_node = curr_node

        chrm_end_node.append(prev_node)
        chrm_end_c_node.append(prev_c_node)
        node_orders.append(node_order)
        chrm_end_nodes.append(chrm_end_node)
        chrm_end_c_nodes.append(chrm_end_c_node)

    return node_orders, node_lengths, chrm_end_nodes, chrm_end_c_nodes
