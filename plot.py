from globalVariables import *
import matplotlib.pyplot as plt
plt.switch_backend('agg')

def plot():
	inputGs = [G.split("/")[-1]+".bed" for G in inputGenomes]
	IN1 = open(outBEDConsensus, "r")

	totalLen = 0
	chrmEnds = list()
	lengths = dict()
	consensus = list()
	prevChr = "chr1"
	for line in IN1:
		info = line.rstrip().split()
		currChr = info[0]
		node = info[3]
		length = int(info[2]) - int(info[1])
		lengths[node] = length
		totalLen += length
		if currChr.startswith("chr"):
			consensus.append(node)
			if currChr != prevChr:
				chrmEnds.append(node)
		prevChr = currChr

	Xcoords = {}
	start = 0
	end = 0
	for node in consensus:
		end = start + lengths[node]
		Xcoords[node] = [start, end]
		start = end+1


	colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
	colorI = 0
	Ystarts = [x*totalLen/20 for x in range(len(inputGs))]
	YSI = 0
	for inputG in inputGs:
		INfile = open(inputG, "r")
		query = list()
		for line in INfile:
			info = line.rstrip().split()
			node = info[3]
			if info[0].startswith("chr") and node.startswith("C"):
				query.append(node)

		Ystart = Ystarts[YSI]
		YSI += 1
		xpairs_C = []
		ypairs_C = []
		
		for node in query:
			if node in consensus:
				Yend = Ystart + lengths[node]
				Xstart = Xcoords[node][0]
				Xend = Xcoords[node][1]
				xpairs_C.append([Xstart, Xend])
				ypairs_C.append([Ystart, Yend])
				Ystart = Yend
			else:
				Ystart += lengths[node]

		call_list_C = []
		for xends,yends in zip(xpairs_C,ypairs_C):
			call_list_C.append(xends)
			call_list_C.append(yends)
			call_list_C.append(colors[colorI%len(colors)])
		plt.plot(*call_list_C)	
		colorI += 1

	for node in chrmEnds:
		Xstart = Xcoords[node][0]
		plt.axvline(x=Xstart)

	plt.xticks([], [])
	plt.yticks([], [])
	plt.savefig('out.png', format='png', dpi=1e3)
