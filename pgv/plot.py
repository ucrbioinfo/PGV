from .global_variables import *
import matplotlib.pyplot as plt

def plot(input_genomes):
	input_gs = [G.split("/")[-1]+".bed" for G in input_genomes]
	in1 = open(outBEDConsensus, "r")

	total_len = 0
	chrm_ends = list()
	lengths = dict()
	consensus = list()
	prev_chr = "chr1"
	for line in in1:
		info = line.rstrip().split()
		curr_chr = info[0]
		node = info[3]
		length = int(info[2]) - int(info[1])
		lengths[node] = length
		total_len += length
		if curr_chr.startswith("chr"):
			consensus.append(node)
			if curr_chr != prev_chr:
				chrm_ends.append(node)
		prev_chr = curr_chr

	x_coords = {}
	start = 0
	end = 0
	for node in consensus:
		end = start + lengths[node]
		x_coords[node] = [start, end]
		start = end+1


	colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22",
			  "#17becf"]
	color_i = 0
	y_starts = [x*total_len/20 for x in range(len(input_gs))]
	ysi = 0
	for inputG in input_gs:
		i_nfile = open(inputG, "r")
		query = list()
		for line in i_nfile:
			info = line.rstrip().split()
			node = info[3]
			if info[0].startswith("chr") and node.startswith("C"):
				query.append(node)

		y_start = y_starts[ysi]
		ysi += 1
		x_pairs_c = []
		y_pairs_c = []

		for node in query:
			if node in consensus:
				y_end = y_start + lengths[node]
				x_start = x_coords[node][0]
				x_end = x_coords[node][1]
				x_pairs_c.append([x_start, x_end])
				y_pairs_c.append([y_start, y_end])
				y_start = y_end
			else:
				y_start += lengths[node]

		call_list_c = []
		for x_ends, y_ends in zip(x_pairs_c, y_pairs_c):
			call_list_c.append(x_ends)
			call_list_c.append(y_ends)
			call_list_c.append(colors[color_i % len(colors)])
		plt.plot(*call_list_c)
		color_i += 1

	for node in chrm_ends:
		x_start = x_coords[node][0]
		plt.axvline(x=x_start)

	plt.xticks([], [])
	plt.yticks([], [])
	plt.show()
