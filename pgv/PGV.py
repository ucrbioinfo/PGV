import sys
import re
import numpy
from . import process_xmfa
from . import get_consensus
from . import get_bed
from . import plot
from . import config_parser


def pgv():
    genome_files, xmfa_file, num_of_chrms, aln_score_threshold, bed_aligned, out_bed_consensus, \
    color_consensus, color_c, color_crev, color_ctrans, color_p, color_u = config_parser.parse_config_file()

    nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes = process_xmfa.process_xmfa(genome_files, xmfa_file, num_of_chrms)
    print("Finished processing multiple sequence alignments")

    consensus = get_consensus.get_consensus(nodeOrders, chrmEndCNodes, genome_files, aln_score_threshold)
    print("Built consensus sucessfully")

    get_bed.get_bed(consensus, nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes, genome_files, num_of_chrms,
                    bed_aligned, out_bed_consensus, color_consensus, color_c, color_crev, color_ctrans, color_p, color_u)
    print("Generated output BED files. Please visit pgv.cs.ucr.edu to view these.")

    plot.plot(genome_files, out_bed_consensus)
    print("Generated dotplots between each assembly and consensus sequence")
