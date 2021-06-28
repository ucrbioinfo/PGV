from globalVariables import *

import numpy
import sys
from collections import Counter
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, LocalSequenceAligner


def merge(CnodeOrders, linked):
	sys.setrecursionlimit(len(CnodeOrders[0]))
	vocabulary = Vocabulary()
	scoring = SimpleScoring(1, -1)
	aligner = LocalSequenceAligner(scoring, -1)
	encodedOrders = [vocabulary.encodeSequence(Sequence(CnodeOrder)) for CnodeOrder in CnodeOrders]
	loc2key = dict()
	locations = list()
	linkedNew = dict()

	while bool(linked):
		key, path = linked.popitem()
		if key != path[0]:
			continue
		encodedPath = vocabulary.encodeSequence(Sequence(path))
		encodedPathRev = vocabulary.encodeSequence(Sequence(path[::-1]))
		scores = list()
		scoresRev = list()
		alnLoc = list()
		alnLocRev = list()

		for i in range(numOfGenomes):
			encodedOrder = encodedOrders[i]
			CnodeOrder = CnodeOrders[i]
			score = aligner.align(encodedOrder, encodedPath, backtrace=False)
			scores.append(score)
			alnLoc.append(CnodeOrder.index(path[int(len(path)/2)]))

			scoreRev = aligner.align(encodedOrder, encodedPathRev, backtrace=False)
			scoresRev.append(scoreRev)
			alnLocRev.append(CnodeOrder.index(path[len(path)-int(len(path)/2)-1]))

		sumScore = sum(scores)
		sumScoreRev = sum(scoresRev)
		if sumScoreRev > sumScore:
			alnLoc = alnLocRev
			path = path[::-1]
		maxScore = sum([max(scores[i], scoresRev[i]) for i in range(len(scores))])
		if maxScore >= alnScoreThr * numOfGenomes* len(path):
			topLoc = numpy.average(alnLoc)
			while topLoc in locations:
				topLoc += 0.0001
			locations.append(topLoc)
			loc2key[topLoc] = key
			linkedNew[key] = path
		else:
			alignments = list()
			for i in range(numOfGenomes):
				encodedOrder = encodedOrders[i]
				CnodeOrder = CnodeOrders[i]
				score, encodeds = aligner.align(encodedOrder, encodedPath, backtrace=True)
				alignment = vocabulary.decodeSequenceAlignment(encodeds[0])
				alignments.append(alignment)
			starts = list()
			ends = list()
			for aln in alignments:
				leftBound = path.index(aln[0][1])
				rightBound = path.index(aln[-1][1])
				unAlnLen = len(path) - abs(rightBound - leftBound + 1)
				misMatchLen, start, end = findMaxMismatch(aln, path)
				if misMatchLen > unAlnLen:
					starts.append(start)
					ends.append(end)
				else:
					starts.append(min(leftBound, rightBound))
					ends.append(max(leftBound, rightBound))
			start = Counter(starts).most_common(1)[0][0]
			end = Counter(ends).most_common(1)[0][0]
			if start > end:
				temp = start
				start = end
				end = temp
			paths = [path[:start], path[start:end+1], path[end+1:]]
			if start == 0 and end == len(path) -1: ## could not cut
				topLoc = numpy.average(alnLoc)
				while topLoc in locations:
					topLoc += 0.0001
				locations.append(topLoc)
				loc2key[topLoc] = key
				linkedNew[key] = path
			else:
				for curr in paths:
					if curr:
						linked[curr[0]] = curr

	consensus = []
	locations.sort()
	for location in locations:
		key = loc2key[location]
		consensus += linkedNew[key]
	return consensus

				
def findMaxMismatch(aln, path):
	currLen = maxLen = 0
	currS = currE = maxS = maxE = 0
	for i in range(len(aln)):
		if aln[i][0] != aln[i][1]:
			currLen += 1
			currE = i
		else:
			if currLen > maxLen:
				maxS = currS
				maxE = currE
				maxLen = currLen
			currLen = 0
			currS = i+1
	if currLen > maxLen:
		maxS = currS
		maxE = currE
		maxLen = currLen

	while(aln[maxS][1]=='-'):
		maxS += 1
		maxLen -= 1
	while(aln[maxE][1]=='-'):
		maxE -= 1
		maxLen -= 1

	return (maxLen, path.index(aln[maxS][1]), path.index(aln[maxE][1]))

