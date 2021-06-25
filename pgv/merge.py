import numpy
import sys
from collections import Counter
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, LocalSequenceAligner


def merge(c_node_orders, linked, input_genomes, aln_score_thr):
	sys.setrecursionlimit(len(c_node_orders[0]))
	vocabulary = Vocabulary()
	scoring = SimpleScoring(1, -1)
	aligner = LocalSequenceAligner(scoring, -1)
	encoded_orders = [vocabulary.encodeSequence(Sequence(CnodeOrder)) for CnodeOrder in c_node_orders]
	loc2key = dict()
	locations = list()
	linked_new = dict()

	while bool(linked):
		key, path = linked.popitem()
		if key != path[0]:
			continue
		encoded_path = vocabulary.encodeSequence(Sequence(path))
		encoded_path_rev = vocabulary.encodeSequence(Sequence(path[::-1]))
		scores = list()
		scores_rev = list()
		aln_loc = list()
		aln_loc_rev = list()

		for i in range(len(input_genomes)):
			encoded_order = encoded_orders[i]
			c_node_order = c_node_orders[i]
			score = aligner.align(encoded_order, encoded_path, backtrace=False)
			scores.append(score)
			aln_loc.append(c_node_order.index(path[int(len(path)/2)]))

			score_rev = aligner.align(encoded_order, encoded_path_rev, backtrace=False)
			scores_rev.append(score_rev)
			aln_loc_rev.append(c_node_order.index(path[len(path)-int(len(path)/2)-1]))

		sum_score = sum(scores)
		sum_score_rev = sum(scores_rev)
		if sum_score_rev > sum_score:
			aln_loc = aln_loc_rev
			path = path[::-1]
		max_score = sum([max(scores[i], scores_rev[i]) for i in range(len(scores))])
		if max_score >= aln_score_thr * len(input_genomes) * len(path):
			top_loc = numpy.average(aln_loc)
			while top_loc in locations:
				top_loc += 0.0001
			locations.append(top_loc)
			loc2key[top_loc] = key
			linked_new[key] = path
		else:
			alignments = list()
			for i in range(len(input_genomes)):
				encoded_order = encoded_orders[i]
				c_node_order = c_node_orders[i]
				score, encodeds = aligner.align(encoded_order, encoded_path, backtrace=True)
				alignment = vocabulary.decodeSequenceAlignment(encodeds[0])
				alignments.append(alignment)
			starts = list()
			ends = list()
			for aln in alignments:
				left_bound = path.index(aln[0][1])
				right_bound = path.index(aln[-1][1])
				un_aln_len = len(path) - abs(right_bound - left_bound + 1)
				mis_match_len, start, end = find_max_mismatch(aln, path)
				if mis_match_len > un_aln_len:
					starts.append(start)
					ends.append(end)
				else:
					starts.append(min(left_bound, right_bound))
					ends.append(max(left_bound, right_bound))
			start = Counter(starts).most_common(1)[0][0]
			end = Counter(ends).most_common(1)[0][0]
			if start > end:
				temp = start
				start = end
				end = temp
			paths = [path[:start], path[start:end+1], path[end+1:]]
			if start == 0 and end == len(path) -1: ## could not cut
				top_loc = numpy.average(aln_loc)
				while top_loc in locations:
					top_loc += 0.0001
				locations.append(top_loc)
				loc2key[top_loc] = key
				linked_new[key] = path
			else:
				for curr in paths:
					if curr:
						linked[curr[0]] = curr

	consensus = []
	locations.sort()
	for location in locations:
		key = loc2key[location]
		consensus += linked_new[key]
	return consensus


def find_max_mismatch(aln, path):
	curr_len = max_len = 0
	curr_s = curr_e = max_s = max_e = 0
	for i in range(len(aln)):
		if aln[i][0] != aln[i][1]:
			curr_len += 1
			curr_e = i
		else:
			if curr_len > max_len:
				max_s = curr_s
				max_e = curr_e
				max_len = curr_len
			curr_len = 0
			curr_s = i+1
	if curr_len > max_len:
		max_s = curr_s
		max_e = curr_e
		max_len = curr_len

	while aln[max_s][1] == '-':
		max_s += 1
		max_len -= 1
	while aln[max_e][1] == '-':
		max_e -= 1
		max_len -= 1

	return max_len, path.index(aln[max_s][1]), path.index(aln[max_e][1])
