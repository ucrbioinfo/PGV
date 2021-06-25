import sys
import re
import numpy
from .process_xmfa import process_xmfa
from .get_consensus import get_consensus
from .get_bed import get_bed
from .plot import plot
from .input_parser import parse_input

genome_files, xmfa_file, num_of_chrms, aln_score_threshold, bed_aligned = parse_input()

nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes = process_xmfa(genome_files, xmfa_file, num_of_chrms)
print("Finished processing multiple sequence alignments")

consensus = get_consensus(nodeOrders, chrmEndCNodes, genome_files, aln_score_threshold)
print("Built consensus sucessfully")

get_bed(consensus, nodeOrders, nodeLengths, chrmEndNodes, chrmEndCNodes, genome_files, num_of_chrms, bed_aligned)
print("Generated output BED files. Please visit pgv.cs.ucr.edu to view these.")

plot(genome_files)
print("Generated dotplots between each assembly and consensus sequence")
