import sys
import os
from configparser import ConfigParser


def parse_config_file():
    user_input = input("Please provide the file path of the PGV config file. See detailed explanation and an example"
                       " of the config file on https://github.com/qihualiang/PanViz\n"
                       "Please enter full file path: ")
    while not os.path.exists(user_input):
        user_input = input("file doesn't exist, please re-enter the file path: ")
    parser = ConfigParser()
    parser.read(user_input)

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
