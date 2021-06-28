from collections import Counter

## return [1st, 2nd] or [1st]
def getTop2(neighbors):
	res = []
	top3 = Counter(neighbors).most_common(3)

	## only one node in neighbors
	if len(top3) == 1: 
		res = [top3[0][0]]
	## only two nodes in neighbors
	elif len(top3) == 2:
		res = [top3[0][0], top3[1][0]]
	## >= 3 nodes
	else:
		## 2nd > 3rd --> no tie for top2
		if top3[1][1] > top3[2][1]:
			res = [top3[0][0], top3[1][0]]
		## 2nd = 3rd, check if 1st > 2nd --> no tie for top1
		elif top3[0][1] > top3[1][1]:
			res = [top3[0][0]]

	return res
