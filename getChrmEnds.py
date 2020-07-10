from globalVariables import *

import Bio
from Bio import SeqIO

def getChrmEnds():
	chrmEnds = []
	for inputGenome in inputGenomes:
		INPUT = open(inputGenome,"r")
		chrmEnd = []
		sumLength = 0
		chrmCount = 0
		for chrm in SeqIO.parse(INPUT, "fasta"):
			chrmCount += 1
			sumLength += len(chrm.seq)
			if chrmCount <= numOfChrms:
				chrmEnd.append(sumLength)
		chrmEnd.append(sumLength)
		chrmEnds.append(chrmEnd)

	return chrmEnds

