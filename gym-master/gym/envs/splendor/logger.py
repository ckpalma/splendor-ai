# import train
# import structure as struct
# import game_controller as gc
import sys
import time
import matplotlib.pyplot as plt
import train
from structure import *
from game_controller import *

class Logger():

	def __init__(self):

		self._trainer = train.Trainer()

	def log(self, numberGames):
		print("\nLOGGING\n")
		# store number of rewards per turn for each game
		AI0_graphs = {}
		AI1_graphs = {}
		AI2_graphs = {}
		AI3_graphs = {}
		# store the average number of rewards for each game
		AI0_rew_graphs = []
		AI1_rew_graphs = []
		AI2_rew_graphs = []
		AI3_rew_graphs = []

		rew = [0.,0.,0.,0.]
		aiVers = [0,0,0,0]

		for i in range(numberGames):
			print("\n GAME : " + str(i), end="\r")
			A0, A1, A2, A3 = self._trainer.run_game(False)
			AI0_graphs[str(i)] = A0
			AI1_graphs[str(i)] = A1
			AI2_graphs[str(i)] = A2
			AI3_graphs[str(i)] = A3
			rew, aiVers = self._trainer.calcAverage(rew,aiVers,numberGames)
			AI0_rew_graphs.append(rew[0])
			AI1_rew_graphs.append(rew[1])
			AI2_rew_graphs.append(rew[2])
			AI3_rew_graphs.append(rew[3])



			self._trainer.new_game()
		return {'AI 0' : [AI0_graphs, AI0_rew_graphs], 
				'AI 1' : [AI1_graphs, AI1_rew_graphs],
				'AI 2' : [AI2_graphs, AI2_rew_graphs],
				'AI 3' : [AI3_graphs, AI3_rew_graphs]}

	def graph(self, data_dict, num_games):

		#plotting rewards per turn for each game
		for i in range(num_games):
			# fig, ax = plt.subplots()
			# fig.canvas.set_window_title('Rewards per turn: Game ' + str(i))
			# ax.plot(range(len(data_dict['AI 0'][0][str(i)])), data_dict['AI 0'][0][str(i)], label = 'AI 0')
			# ax.plot(range(len(data_dict['AI 1'][0][str(i)])), data_dict['AI 1'][0][str(i)], label = 'AI 1')
			# ax.plot(range(len(data_dict['AI 2'][0][str(i)])), data_dict['AI 2'][0][str(i)], label = 'AI 2')
			# ax.plot(range(len(data_dict['AI 3'][0][str(i)])), data_dict['AI 3'][0][str(i)], label = 'AI 3')

			# legend = ax.legend(loc='upper left')

			# plt.xlabel('turn number')
			# plt.ylabel('rewards')

			# plt.show()

			plt.figure('Rewards per turn: Game ' + str(i))

			plt.xlabel('turn number')
			plt.ylabel('rewards')
			plt.plot(range(len(data_dict['AI 0'][0][str(i)])), data_dict['AI 0'][0][str(i)], label = 'AI 0')
			plt.plot(range(len(data_dict['AI 1'][0][str(i)])), data_dict['AI 1'][0][str(i)], label = 'AI 1')
			plt.plot(range(len(data_dict['AI 2'][0][str(i)])), data_dict['AI 2'][0][str(i)], label = 'AI 2')
			plt.plot(range(len(data_dict['AI 3'][0][str(i)])), data_dict['AI 3'][0][str(i)], label = 'AI 3')
			plt.legend()
			plt.show()

		#plotting rewards per game

		plt.figure('Rewards per game')
		plt.plot(range(num_games), data_dict['AI 0'][1], label = 'AI 0')
		plt.plot(range(num_games), data_dict['AI 1'][1], label = 'AI 1')
		plt.plot(range(num_games), data_dict['AI 2'][1], label = 'AI 2')
		plt.plot(range(num_games), data_dict['AI 3'][1], label = 'AI 3')
		plt.legend()
		plt.xlabel('Turn')
		plt.ylabel('Reward Total')
		plt.show()

		# fig, ax = plt.subplots()
		# fig.canvas.set_window_title('Rewards per game')
		# ax.plot(range(len(num_games)), data_dict['AI 0'][1], label = 'AI 0')
		# ax.plot(range(len(num_games)), data_dict['AI 1'][1], label = 'AI 1')
		# ax.plot(range(len(num_games)), data_dict['AI 2'][1], label = 'AI 2')
		# ax.plot(range(len(10)), data_dict['AI 3'][1], label = 'AI 3')

		# legend = ax.legend(loc='upper left')

		# plt.xlabel('game number')
		# plt.ylabel('rewards per game')

		# plt.show()




logger = Logger()
gameNumberVar = 3
data_dict = logger.log(gameNumberVar)
logger.graph(data_dict, gameNumberVar)




