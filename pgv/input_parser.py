import sys
import os
from collections import OrderedDict


def parse_input():
    genome_files = parse_genome_files()
    xmfa_file = parse_xmfa_file()
    num_of_chrms = parse_number_of_chromosomes()
    aln_score_threshold = parse_aln_score_threshold()
    bed_aligned = parse_bed_aligned()
    return genome_files, xmfa_file, num_of_chrms, aln_score_threshold, bed_aligned


def parse_genome_files():
    file_paths = []
    while True:
        user_input = input("Enter a genome file path: ")
        while not os.path.exists(user_input):
            user_input = input("file doesn't exist, please re-enter the file path: ")
        file_paths.append(user_input)
        if input("Enter another file? [Y/N]: ") == "N":
            return list(OrderedDict.fromkeys(file_paths))


def parse_xmfa_file():
    user_input = input("Enter the file path of the output file of ProgressiveMauve: ")
    while not os.path.exists(user_input):
        user_input = input("file doesn't exist, please re-enter the file path: ")
    return user_input


def parse_number_of_chromosomes():
    while True:
        try:
            num = int(input("Please enter number of chromosomes to be considered: "))
        except ValueError:
            print("Invalid number")
            continue
        else:
            return num


def parse_aln_score_threshold():
    if input("Use default alignment Threshold for alignment scores (0.7) ? [Y/N]: ") == "Y":
        return 0.7
    while True:
        try:
            num = float(input("Please enter alignment score threshold: "))
        except ValueError:
            print("Invalid number")
            continue
        else:
            return num


def parse_bed_aligned():
    while True:
        user_input = input("Do you want to align core blocks in accession with corresponding core blocks in "
                           "consensus [Y/N]? : ")
        if user_input == "Y":
            return True
        elif user_input == "N":
            return False
        else:
            continue

