import numpy as np
from tqdm import tqdm
import preCalc

N = 17

class AntSystem:
	def __init__(self, rho,alpha,beta, ants = 1000, max_gens = 10000):
		self.rho = rho
		self.alpha = alpha
		self.beta = beta

		self.ants = ants
		self.max_gens = max_gens

		self.adj = preCalc.getAdj()
		self.heu = preCalc.getHeu(self.adj)

		self.tau = []
		self.L = []
		self.used_edge = []
		self.p = []
		self.visited = []
		self.totalVisit = 1
		self.minTau = [[(0.009) for i in range(N)] for j in range(N)]

	def init_gen(self):
		self.L = np.zeros((self.ants))
		self.used_edge = [[] for i in range(self.ants)]

		self.p = np.power(self.tau, self.alpha) * np.power(self.heu, self.beta)

		for i in range(N):
			self.p[i] = self.p[i] / np.sum(self.p[i])
			# assert(np.sum(self.p[i]) == 1.)

	def deleteStuff(self):
		del self.L
		del self.used_edge
		del self.p 
		del self.visited
		del self.totalVisit

	def getNextNode(self,i):
		j = np.random.choice(N, p=self.p[i])
		while self.visited[j] == True:
			j = np.random.choice(N, p=self.p[i])
		return j

	def simulate(self, k):
		self.visited = [False for i in range(N)]

		currNode = np.random.randint(0,N-1)
		start = currNode
		self.visited[currNode] = True
	
		for self.totalVisit in range(1,N):
			j = self.getNextNode(currNode)
			self.L[k] += self.adj[currNode][j]
			self.used_edge[k].append((currNode,j))
			self.visited[j] = True
			currNode = j

		self.L[k] += self.adj[currNode][start]
		return self.L[k]

	def updatePheromone(self):
		deltaTau = np.zeros((N,N))
		for k in range(self.ants):
			for (i,j) in self.used_edge[k]:
				deltaTau[i][j] += 2085/self.L[k]
				deltaTau[j][i] += 2085/self.L[k]

		self.tau = ((1 - self.rho) * self.tau) + deltaTau
		del deltaTau

		np.maximum(self.tau, self.minTau, self.tau)

	# returns the generation that finds the best solution, or (self.max_gens*2) if can't find in self.max_gens
	def runOnce(self, s):
		ans = 2085 * 69
		self.tau = np.ones((N,N))

		np.random.seed(seed = s)
		for gen in tqdm(range(self.max_gens)):
			self.init_gen()
			for ant in range(self.ants):
				self.simulate(ant)
			# print("\nAnts Done")
			ans = min(ans, min(self.L))
			self.updatePheromone()
			# print("Pheromone Updated")
			self.deleteStuff()

			if(ans == 2085):
				return gen
		return self.max_gens*2
		# minimum tour for gr17 has length 2085, btw.

	# runOnce() multiple times, with constant seeding
	def runMultiple(self, number_of_runs = 100):
		results = np.zeros((number_of_runs))
		
		# seed = [69420, 177013, 22028009, 21032004, 22028013, 8012004, 3103,20] 
		np.random.seed(seed = 69420)
		seed = [np.random.randint(0,30005) for i in range(number_of_runs)]

		for run in range(number_of_runs):
			results[run] = self.runOnce(seed[run])
		return results

# a = AntSystem(0.05,1,2, 200,1000)
# print(a.runMultiple())