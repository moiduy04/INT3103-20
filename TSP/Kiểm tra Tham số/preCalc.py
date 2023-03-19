import numpy as np

N = 17

# I don't use 1/d_ij as heuristic 'cause I want to normalize it
# So it's actually (1/d_ij) / (sum of all 1/d_ij's)

# I'm also gonna call it 'h' or 'heu' intead of the Greek letter 'eta'

# Heuristic alg ineffient as hell, but good enough.
def getHeu(adj):
	h = np.zeros((N,N))
	for i in range(N):
		total = 0
		for j in range(N):
			d_ij = adj[i][j]
			if (d_ij != 0):
				total += 10000./d_ij

		for j in range(N):
			d_ij = adj[i][j]
			if (d_ij != 0):
				h[i][j] = (10000./d_ij) / (total)
			else:
				h[i][j] = 0
	return h

def isNum(c):
	zero = ord('0')
	nine = ord('9')
	c = ord(c)
	return (zero <= c and c <= nine)

def getAdj():
	adj = np.zeros((N,N))
	with open("gr17_d.txt") as file:
	    contents = file.read()
	    num = -1
	    order = 0
	    for c in contents:
	    	if isNum(c) == True:
	    		num = max(num,0)
	    		num = (num*10) + ord(c)-ord('0')
	    	elif num >= 0:
	    		i = order // N
	    		j = order %  N
	    		adj[i][j] = num
	    		num = -1
	    		order += 1
	    file.close()
	return adj

# adj = getAdj()
# heu = getHeu(adj)
# print(adj, end = '\n\n\n')
# print(heu, end = '\n\n\n')