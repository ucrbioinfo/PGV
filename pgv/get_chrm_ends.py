import Bio
from Bio import SeqIO


def get_chrm_ends(input_genomes, num_of_chrms):
	chrm_ends = []
	for input_genome in input_genomes:
		input_file = open(input_genome, "r")
		chrm_end = []
		sum_length = 0
		chrm_count = 0
		for chrm in SeqIO.parse(input_file, "fasta"):
			chrm_count += 1
			sum_length += len(chrm.seq)
			if chrm_count <= num_of_chrms:
				chrm_end.append(sum_length)
		chrm_end.append(sum_length)
		chrm_ends.append(chrm_end)

	return chrm_ends

