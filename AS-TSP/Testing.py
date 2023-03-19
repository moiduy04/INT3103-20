import numpy as np
import ACO

#https://en.wikipedia.org/wiki/Ant_colony_optimization_algorithms

# pheromone evaporation coefficient tests (7 tests)
rho_tests = [0.0, 0.05, 0.25, 0.5, 0.75, 0.99, 1]

# edge selection formula tests (1x2 = 2 tests)
alpha_tests = [1] 
beta_tests  = [1,2]
edge_select_tests  = list((i,j) for i in alpha_tests for j in beta_tests)
# edge selection = rho(i,j)^alpha + heu(i,j)^beta

# parameters unchanged throughout execution of algorithm.

# we will have ?? data points

results = []
idx = 0

tests = []
for rho in rho_tests:
	for (alpha,beta) in edge_select_tests:
		tests.append((rho,(alpha,beta)))
		results.append([])

tests[11], tests[13] = tests[13], tests[11]

print(tests)

for idx in range(11,14):
	rho,(alpha,beta) = tests[idx]
	a = ACO.AntSystem(rho, alpha, beta, 200, 1000)
	results[idx] = a.runMultiple(100)
	print(f'----- ({rho},({alpha},{beta})) ----- {idx}: {results[idx]}')


print(tests, end = "\n\n\n")
print(results)

for idx in range(14):
	rho,(alpha,beta) = tests[idx]
	print(f'----- ({rho},({alpha},{beta})) ----- {idx}: {results[idx]}')

