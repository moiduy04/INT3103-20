import numpy as np
import tkinter as tk
from tqdm import tqdm #progress bar
import sys
import random as rand


EMPTY = 0
BODY = 1
HEAD = 5
FOOD = 100

UP =   (-1,0)
DOWN  = (1,0)
LEFT = (0,-1)
RIGHT = (0,1)

DIRECTION = [UP,DOWN,LEFT,RIGHT]

def mv(x,y):
	return (x[0]+y[0],x[1]+y[1])

def reLu(x):
	return x * (x > 0)

def np_rand(r,c):
	return ((np.random.rand(r,c)*2) -1)


class Gene:
	def __init__(self, size, randomize, g = None):
		self.size = size
		self.snake_pos = [(self.size//2-1, self.size//2-2)]
		for i in range(2):
			self.snake_pos.append(mv(self.snake_pos[-1],RIGHT))

		if randomize == True:
			self.A1 = np_rand(8,12)
			self.A2 = np_rand(4,8)
			self.b1 = np_rand(8,1)
			self.b2 = np_rand(4,1)
		else:
			self.A1 = g.A1
			self.A2 = g.A2
			self.b1 = g.b1
			self.b2 = g.b2

	def move(self, in_layer):
		Y = reLu(np.matmul(self.A1,in_layer) + self.b1)
		return np.argmax(np.matmul(self.A2,Y) + self.b2)


class Game:
	def __init__(self, size, num_snakes, max_gen):
		self.size = size
		self.max_turn = 69420
		self.max_gen  = max_gen
		self.num_snakes = num_snakes
		
		self.snake = [Gene(size, True) for i in range(self.num_snakes)]
		self.snake_ids = [i for i in range(self.num_snakes)]
		
		self.food_amount = 1
		self.food_pos = (0,0)

		self.roulette_value = 0 
		self.roulette_table = []
		
		self.board = np.zeros([self.size, self.size])
		self.last_move = 3
		self.in_layer = None

		self.gen_fitness = [0 for i in range(max_gen)]

	def update_board(self, pos, val):
		self.board[pos[0]][pos[1]] = val
	def board_val(self, pos):
		return self.board[pos[0]][pos[1]]
	def get_new_food(self):
		self.food_pos = (rand.randint(0,self.size-1),rand.randint(0,self.size-1))
		while(self.board_val(self.food_pos) != EMPTY):
			self.food_pos = (rand.randint(0,self.size-1),rand.randint(0,self.size-1))
		self.update_board(self.food_pos, FOOD)

	def get_data(self, i, move, idx):
		head_pos = mv(self.snake[i].snake_pos[-1], move)
		dist_wall = 1
		dist_body = 100
		dist_food = 100
		while (0 <= min(head_pos) and max(head_pos) < self.size):
			if self.board_val(head_pos) == BODY:
				dist_body = min(dist_body, dist_wall)
			elif self.board_val(head_pos) == FOOD:
				dist_food = min(dist_food, dist_wall)
			head_pos = mv(head_pos, move)
			dist_wall += 1

		if dist_body == 100:
			dist_body = 0
		if dist_food == 100:
			dist_food = 0

		self.in_layer[3*idx]    = dist_wall/self.size
		self.in_layer[3*idx +1] = dist_body/self.size
		self.in_layer[3*idx +2] = dist_food/self.size

	def update(self, i, move):
		eaten_flag = False
		self.last_move = move
		head_pos = mv(self.snake[i].snake_pos[-1], DIRECTION[move])

		if min(head_pos) < 0 or self.size <= max(head_pos):
			return False, eaten_flag #DEAD

		self.update_board(self.snake[i].snake_pos[-1], BODY)

		if self.board_val(head_pos) == FOOD:
			eaten_flag = True
			self.get_new_food()
		else:
			self.update_board(self.snake[i].snake_pos[0], EMPTY)
			self.snake[i].snake_pos.pop(0)

		if self.board_val(head_pos) == BODY:
			return False, eaten_flag #DEAD

		self.snake[i].snake_pos.append(head_pos)
		self.update_board(self.snake[i].snake_pos[-1], HEAD)
		return True, eaten_flag #ALIVE

	def simulate(self, i):
		self.board = np.zeros([self.size, self.size])

		for j in self.snake[i].snake_pos:
			self.update_board(j, BODY)
		self.update_board(self.snake[i].snake_pos[-1], HEAD)

		for _ in range(self.food_amount):
			self.get_new_food()

		last_eaten = 0
		for turn in range(0,self.max_turn):
			self.in_layer = np.empty([12,1])
			tmp = 0
			for move in range(4):
				self.get_data(i, DIRECTION[move], tmp)
				tmp += 1

			alive_flag, eaten_flag = self.update(i, self.snake[i].move(self.in_layer))
			if alive_flag == False:
				return turn, len(self.snake[i].snake_pos)

			if eaten_flag == False:
				if turn - last_eaten > self.size*self.size:
					return turn, len(self.snake[i].snake_pos)
			elif eaten_flag == True:
				last_eaten = turn
			else:
				assert(False)

		return self.max_turn, len(self.snake[i].snake_pos)

	def roulette(self):
		val = np.random.uniform(0,self.roulette_value)
		for i in self.snake_ids:
			if val < self.roulette_table[i+1]:
				return i
		assert(False)
	def mutation(self, i):
		newI = Gene(self.size, False, self.snake[i])
		match rand.randint(0,5):
			case 0:
				newI.A1[rand.randint(0,7)][rand.randint(0,11)] = np.random.uniform(-1,1)
			case 1:
				newI.A2[rand.randint(0,3)][rand.randint(0, 7)] = np.random.uniform(-1,1)
			case 3:
				newI.b1[rand.randint(0,7)] = np.random.uniform(-1,1)
			case default:
				newI.b2[rand.randint(0,3)] = np.random.uniform(-1,1)
		return newI
	def crossover(self, i, j):
		nf = [Gene(self.size, False, self.snake[i]),
			  Gene(self.size, False, self.snake[j])]

		match rand.randint(0,5):
			case 0:
				nf[0].A1, nf[1].A1 = nf[1].A1, nf[0].A1
			case 1:
				nf[0].A2, nf[1].A2 = nf[1].A2, nf[0].A2
			case 3:
				nf[0].b1, nf[1].b1 = nf[1].b1, nf[0].b1
			case default:
				nf[0].b2, nf[1].b2 = nf[1].b2, nf[0].b2
			
		return nf[rand.randint(0,1)]
	# def reproduce(self, i, j):
		nf = [Gene(self.size, False, self.snake[i]),
			  Gene(self.size, False, self.snake[j])]
		out = rand.randint(0,1)

		match rand.randint(0,5):
			case 0:
				nf[out].A1 = 0.5*(nf[1].A1 + nf[0].A1)
			case 1:
				nf[out].A2 = 0.5*(nf[1].A2 + nf[0].A2)
			case 3:
				nf[out].b1 = 0.5*(nf[1].b1 + nf[0].b1)
			case default:
				nf[out].b2 = 0.5*(nf[1].b2 + nf[0].b2)
			
		return nf[out]

	def one_generation(self, gen_id):
		self.food_amount = 1
		turn_length = []		
		self.roulette_table = [0]
		self.roulette_value = 0

		lmao = 0
		for i in tqdm(self.snake_ids):
			t_e, length = self.simulate(i)
			
			Eval = t_e + 2**length 
			#print(f'snake {i}: t_e,len = {t_e}, {length} ---> {Eval}')

			self.roulette_table.append(Eval)
			self.roulette_value += Eval

			turn_length.append(t_e)
			lmao = max(lmao, length)

		for i in range(1,len(self.roulette_table)):
			self.roulette_table[i] += self.roulette_table[i-1]

		new_snake = []
		k = int(self.num_snakes // 2)
		for i in range(k):
			new_snake.append(Gene(self.size, False, self.snake[self.roulette()]))

		for i in range(k,self.num_snakes):
			tmp = rand.randint(1,100)
			if tmp <= 5:
				new_snake.append(Gene(self.size, True))
			elif tmp <= 6:
				new_snake.append(self.crossover(self.roulette(),self.roulette()))
			else:
				new_snake.append(self.mutation(self.roulette()))		
				
		del self.snake
		self.snake = new_snake

		assert(len(self.snake) == self.num_snakes)

		self.roulette_table.sort()
		turn_length.sort()
		self.gen_fitness[gen_id] = (self.roulette_value / self.num_snakes, lmao, sum(turn_length)/self.num_snakes)

	def train(self):
		for i in range(self.max_gen):
			self.curr_gen = i
			self.one_generation(i)
			# print(f'\nGENERATION {i}: {self.gen_fitness[i]}')
			print(i,end = ' ')
			for k in self.gen_fitness[i]:
				print(k, end = ' ')
			print()

	def debug(self, i = 0):
		self.board = np.zeros([self.size, self.size])

		for j in self.snake[i].snake_pos:
			self.update_board(j, BODY)
		self.update_board(self.snake[i].snake_pos[-1], HEAD)
		self.update_board(mv(self.snake[i].snake_pos[-1],UP), FOOD)
		print(self.board)

		for _ in range(2):
			print('DATA')
			self.in_layer = self.in_layer = np.empty([12,1])
			for move in range(4):
				self.get_data(i,move)
			print(self.in_layer)

			MOVE = self.snake[i].move(self.in_layer)
			print(f'MOVE\n{MOVE}')
			print(self.update(i,MOVE))
			print(self.board)


a = Game(10,1000,2000)

original_stdout = sys.stdout
with open('RawData.txt', 'w') as f:
	sys.stdout = f
	a.train()
	sys.stdout = original_stdout

print("done")
