from collections import Counter

gap = 0


def get_bed(consensus, node_orders, node_lengths, chrm_end_nodes, chrm_end_c_nodes, input_genomes, num_of_chrms,
            bed_aligned, out_bed_consensus, color_consensus, color_c, color_crev, color_ctrans, color_p, color_u):
    num_of_genomes = len(input_genomes)
    #### get consensus end Cnodes
    consensus_end_c_nodes = list()
    for i in range(num_of_chrms):
        candidate_c_nodes = list()
        for j in range(num_of_genomes):
            candidate_c_nodes.append(chrm_end_c_nodes[j][i])
        occurences = Counter(candidate_c_nodes)
        consensus_end_c_nodes.append(occurences.most_common(1)[0][0])

    #### insert dummy into consensus/nodeOrder
    consensus_whead = ["dummy"]  # consensusWhead = dummy, chr1, dummy, chr2... dummy, contigs
    for c_node in consensus:
        consensus_whead.append(c_node)
        if c_node in consensus_end_c_nodes:
            consensus_whead.append("dummy")
    consensus_whead.append("dummy")

    all_c_nodes = list()
    node_orders_whead = list()
    for i in range(num_of_genomes):
        node_order = node_orders[i]
        c_nodes = list()
        chrm_end_node = chrm_end_nodes[i]
        node_order_whead = ["dummy"]
        for node in node_order:
            node_order_whead.append(node)
            if node.startswith("C"):
                c_nodes.append(node)
            if node in chrm_end_node:
                node_order_whead.append("dummy")
                c_nodes.append("dummy")
        c_nodes.append("dummy")
        node_order_whead.append("dummy")
        all_c_nodes.append(c_nodes)
        node_orders_whead.append(node_order_whead)

    #### initalize interval from consensus input
    intervals = dict()  ## intervals[interval] = max length within this interval
    for i in range(len(consensus_whead)):
        curr_node = consensus_whead[i]
        if curr_node.startswith("C"):
            interval = (consensus_whead[i - 1], consensus_whead[i])
            intervals[interval] = 0

    #### update intervals
    for i in range(num_of_genomes):
        node_order = node_orders_whead[i]
        chrm_end_node = chrm_end_nodes[i]
        prev_node = "dummy"
        lengths_between_interval = 0
        for node in node_order:
            if node.startswith("C"):
                interval = (prev_node, node)
                if interval in intervals and lengths_between_interval > intervals[interval]:
                    intervals[interval] = lengths_between_interval
                lengths_between_interval = 0
                prev_node = node
            elif node.startswith("dummy"):
                lengths_between_interval = 0
                prev_node = node
            else:
                lengths_between_interval += node_lengths[node][i][0] + gap

    #### output consensus BED
    prev_c = dict()
    neighbor_cs_no_direction = dict()
    neighbor_cs_w_direction = dict()
    c_starts = dict()

    start_pos = 1
    chrm_count = 0

    prev = "dummy"

    OUTconsensus = open(out_bed_consensus, "w")
    for i in range(len(consensus_whead)):
        curr_node = consensus_whead[i]
        if curr_node.startswith("C"):
            start_pos += intervals[(prev, curr_node)]
            #endPos = start_pos + max(node_lengths[curr_node])
            endPos = start_pos + max([x[0] for x in node_lengths[curr_node]])
            if chrm_count <= num_of_chrms:
                chrmName = "chr" + str(chrm_count)
            else:
                chrmName = "contigs"
            print(chrmName, start_pos, endPos, curr_node, 1, "+", start_pos, endPos, color_consensus, sep='\t',
                  file=OUTconsensus)
            c_starts[curr_node] = (chrm_count, start_pos)
            prev_c[curr_node] = prev
            neighbor_cs_no_direction[curr_node] = set([prev, consensus_whead[i + 1]])
            neighbor_cs_w_direction[curr_node] = [prev, consensus_whead[i + 1]]
            start_pos = endPos + 1
        else:
            chrm_count += 1
            start_pos = 1
        prev = curr_node

    #### output all BEDs
    for i in range(num_of_genomes):
        outFile = open(input_genomes[i].split("/")[-1] + ".bed", "w")
        node_order_whead = node_orders_whead[i]
        start_pos = 1
        chrm_count = 0
        for j in range(len(node_order_whead)):
            curr_node = node_order_whead[j]
            if chrm_count <= num_of_chrms:
                chrmName = "chr" + str(chrm_count)
            else:
                chrmName = "contigs"

            if curr_node.startswith("C"):
                if bed_aligned and chrm_count == c_starts[curr_node][0] and start_pos < c_starts[curr_node][1]:
                    start_pos = c_starts[curr_node][1]
                endPos = start_pos + node_lengths[curr_node][i][0]
                Cindex = all_c_nodes[i].index(curr_node)
                direction = node_lengths[curr_node][i][1]
                if neighbor_cs_w_direction[curr_node] == [all_c_nodes[i][Cindex - 1],
                                                          all_c_nodes[i][Cindex + 1]]:  ## same prev and next
                    print(chrmName, start_pos, endPos, curr_node, 1, direction, start_pos, endPos, color_c, sep='\t',
                          file=outFile)
                elif neighbor_cs_no_direction[curr_node] == set(
                        [all_c_nodes[i][Cindex - 1], all_c_nodes[i][Cindex + 1]]):  ## rev
                    print(chrmName, start_pos, endPos, curr_node, 1, "-", start_pos, endPos, color_crev, sep='\t',
                          file=outFile)
                else:  ## translocation
                    print(chrmName, start_pos, endPos, curr_node, 1, direction, start_pos, endPos, color_ctrans, sep='\t',
                          file=outFile)
                start_pos = endPos + 1

            elif curr_node.startswith("D"):
                endPos = start_pos + node_lengths[curr_node][i][0]
                direction = node_lengths[curr_node][i][1]
                print(chrmName, start_pos, endPos, curr_node, 1, direction, start_pos, endPos, color_p, sep='\t', file=outFile)
                start_pos = endPos + 1
            elif curr_node.startswith("U"):
                endPos = start_pos + node_lengths[curr_node][i][0]
                direction = node_lengths[curr_node][i][1]
                print(chrmName, start_pos, endPos, curr_node, 1, direction, start_pos, endPos, color_u, sep='\t', file=outFile)
                start_pos = endPos + 1
            else:  ## dummy/Tail
                chrm_count += 1
                start_pos = 1
