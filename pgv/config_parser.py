import sys
import os
from configparser import ConfigParser


def parse_config_file(config_file_path):
    parser = ConfigParser()
    parser.read(config_file_path)

    genome_files = str(parser.get("PGV_CONF", "inputGenomes")).replace('"', '').strip('[').strip(']').replace(' ', '').split(',')
    xmfa_file = str(parser.get("PGV_CONF", "XMFAFile")).replace('"', '')
    num_of_chrms = parser.getint("PGV_CONF", "numOfChrms")
    aln_score_threshold = parser.getfloat("PGV_CONF", "alnScoreThr")
    bed_aligned = parser.getboolean("PGV_CONF", "BEDaligned")
    out_bed_consensus = "PGV.consensus.bed"

    color_consensus = parser.get("PGV_CONF", 'colorConsensus')
    color_c = parser.get("PGV_CONF", 'colorC')
    color_crev = parser.get("PGV_CONF", 'colorCrev')
    color_ctrans = parser.get("PGV_CONF", 'colorCtrans')
    color_p = parser.get("PGV_CONF", 'colorP')
    color_u = parser.get("PGV_CONF", 'colorU')
    return genome_files, xmfa_file, num_of_chrms, aln_score_threshold, bed_aligned, out_bed_consensus, \
           color_consensus, color_c, color_crev, color_ctrans, color_p, color_u
