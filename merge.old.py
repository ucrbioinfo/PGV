from globalVariables import *

import numpy
from collections import Counter
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner


def merge(CnodeOrders, linked):
    vocabulary = Vocabulary()
    scoring = SimpleScoring(1, -1)
    aligner = GlobalSequenceAligner(scoring, -1)

    encodedOrders = [vocabulary.encodeSequence(Sequence(CnodeOrder)) for CnodeOrder in CnodeOrders]
    loc2key = dict()
    locations = list()

    linkedNew = dict()

    while bool(linked):
    	key, path = linked.popitem()
    	if key == path[0]:
            encodedPath = vocabulary.encodeSequence(Sequence(path))
            encodedPathRev = vocabulary.encodeSequence(Sequence(path[::-1]))
            sumScore = sumScoreRev = 0
            alnLoc = alnLocRev = list()
            alns = alnsRev = list()

            for i in range(numOfGenomes):
                encodedOrder = encodedOrders[i]
                CnodeOrder = CnodeOrders[i]
                score, encodeds = aligner.align(encodedOrder, encodedPath, backtrace=True)
                sumScore += score
                alignment = vocabulary.decodeSequenceAlignment(encodeds[0])
                if score == 0: ## if the score is zero, use the location of first node of the path
                    alnLoc.append(CnodeOrder.index(path[0]))
                else: ## use the location of the first aligned node
                    alnLoc.append(CnodeOrder.index(alignment[0][0]))
                    alns.append(alignment)
                score, encodeds = aligner.align(encodedOrder, encodedPathRev, backtrace=True)
                sumScoreRev += score
                alignment = vocabulary.decodeSequenceAlignment(encodeds[0])
                if score == 0: ## if the score is zero, use the location of first node of the reverse path
                    alnLocRev.append(CnodeOrder.index(path[-1]))
                else:
                    alnLocRev.append(CnodeOrder.index(alignment[0][0]))
                    alnsRev.append(alignment)


            if sumScoreRev > sumScore:
                alnLoc = alnLocRev
                path = path[::-1]
                alns = alnsRev

            maxScore = max(sumScore, sumScoreRev)
            if maxScore >= alnScoreThr * len(path):
                avgLoc = numpy.average(alnLoc)
                locations.append(avgLoc)
                loc2key[avgLoc] = key
                linkedNew[key] = path
            else:
                starts = list()
                ends = list()
                for aln in alns:
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

