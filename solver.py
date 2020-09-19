from architecture import *

class Solver(object):
	def __init__(self, game: GameTable) -> None:
		self.game = game
		self.game.update()
		self.height = self.game.rows
		self.width = self.game.columns
		self.model = create_model(self.height, self.width)
		try:
			self.model = load_model_from_file(self.height, self.width)
		except OSError:
			pass

	def train(self, batches: int, game_states: int, epochs: int = 1) -> None:
		# Trains the model with the given number of batches, game_states and epochs
		# The training makes use of the reinforcement learning method.
		# Each prediction represents a probability that a cell contains a mine.
		# We correct each of these predictions: 
		# If the chosen cell didn't contain a mine, we want to tell the network that the probability should be lower, so we replace the cell with a 0
		# Otherwise, we want to tell the network that the probability should be higher, so we replace the cell with a 1
		# After many iterations of this process we end up with a pretty good solver
		print("\n\n\n\n\nTraining with {} game_states, {} batches and {} epochs".format(game_states, batches, epochs))
		current_batch = 0
		while current_batch < batches:
			games_played = 0
			games_won = 0

			train_input_main = np.zeros((game_states, self.height, self.width, 10))
			train_input_secondary = np.zeros((game_states, self.height, self.width, 1))
			train_labels = np.zeros((game_states, self.height, self.width, 1))

			current_game_state = 0
			while current_game_state < game_states:
				self.game.restart_game()
				self.game.left_click(self.width // 2, self.height // 2)
				while self.game.game_over(): # to be sure that the first chosen cell is not containing a mine
					self.game.restart_game()
					self.game.left_click(self.width // 2, self.height // 2)

				while self.game.game_over() == False and current_game_state < game_states:
					training_data_main = get_training_data(self.game, self.height, self.width)
					training_data_secondary = np.array([np.where(training_data_main[0] == 0, 1, 0)])

					train_input_main[current_game_state] = np.einsum("ijk->jki", training_data_main) # changing the input shape from (channels, heigth, width) to (heigth, width, channels)
					train_input_secondary[current_game_state] = np.einsum("ijk->jki", training_data_secondary)

					prediction = self.model.predict([np.array([train_input_main[current_game_state]]), np.array([train_input_secondary[current_game_state]])])
					prediction = prediction[0] # because we're only predicting for a game state
					prediction = np.einsum("ijk->kij", prediction) # make the channel first : shape = (1, heigth, width)
					
					#print(prediction + training_data_main[0])

					training_label = prediction
					prediction = prediction[0] # because we only have one channel as output in the NN's architecture

					lowest_probability = np.where((prediction + training_data_main[0]) == (prediction + training_data_main[0]).min()) # get the lowest probability cell
					best_row = lowest_probability[0][0]
					best_column = lowest_probability[1][0]

					self.game.left_click(best_column, best_row)

					if self.game.game_lost() == True: # update chosen square
						training_label[0, best_row, best_column] = 1 # to 1 if it contained a mine
					else:
						training_label[0, best_row, best_column] = 0 # to 0 otherwise

					training_label = np.einsum("ijk->jki", training_label) # swap the input back to (heigth, width, channels)
					train_labels[current_game_state] = training_label

					current_game_state += 1

			self.model.fit([train_input_main, train_input_secondary], train_labels, epochs = epochs) # train the model
			self.model.save("model.h5") # save the model after each training session

			current_batch += 1

	def test(self, games_to_play: int) -> None:
		# Test the model on a given number of games_to_play
		# This tests the model performance overall
		games_played = 0
		games_won = 0

		while games_played < games_to_play:
			self.game.restart_game()
			self.game.left_click(self.width // 2, self.height // 2)
			while self.game.game_over():
				self.game.restart_game()
				self.game.left_click(self.width // 2, self.height // 2)

			while self.game.game_over() == False:
				main_data = get_training_data(self.game, self.height, self.width)
				secondary_data = np.array([np.where(main_data[0] == 0, 1, 0)])

				prediction = self.model.predict([np.array([np.einsum("ijk->jki", main_data)]), np.array([np.einsum("ijk->jki", secondary_data)])])
				prediction = prediction[0]
				prediction = np.einsum("ijk->kij", prediction)
				prediction = prediction[0]

				lowest_probability = np.where((prediction + main_data[0]) == (prediction + main_data[0]).min())
				best_row = lowest_probability[0][0]
				best_column = lowest_probability[1][0]

				self.game.left_click(best_column, best_row)

			games_played += 1
			if self.game.game_won():
				games_won += 1

		print("Games Played: {}".format(games_played))
		print("Games Won: {}".format(games_won))
		if games_played:
			print("Percent Won: {:.5}%".format((games_won / games_played) * 100))

	def test_past_5_moves(self, games_to_play: int) -> None:
		# Test the model on a given number of games_to_play, but only takes into consideration games that went past 5 moves 
		# (~50% of games are lost because of unlucky moves at the beggining, moves that it needs to do to get relevant information)
		# This tests the model performance in the middle-late game phases
		games_played = 0
		games_won = 0

		while games_played < games_to_play:
			moves = 1
			self.game.restart_game()
			self.game.left_click(self.width // 2, self.height // 2)
			while self.game.game_over():
				self.game.restart_game()
				self.game.left_click(self.width // 2, self.height // 2)

			while self.game.game_over() == False:
				main_data = get_training_data(self.game, self.height, self.width)
				secondary_data = np.array([np.where(main_data[0] == 0, 1, 0)])

				prediction = self.model.predict([np.array([np.einsum("ijk->jki", main_data)]), np.array([np.einsum("ijk->jki", secondary_data)])])
				prediction = prediction[0]
				prediction = np.einsum("ijk->kij", prediction)
				prediction = prediction[0]

				lowest_probability = np.where((prediction + main_data[0]) == (prediction + main_data[0]).min())
				best_row = lowest_probability[0][0]
				best_column = lowest_probability[1][0]

				self.game.left_click(best_column, best_row)
				moves += 1

			if moves > 5:
				games_played += 1
				if self.game.game_won():
					games_won += 1

		print("Games Played: {}".format(games_played))
		print("Games Won: {}".format(games_won))
		if games_played:
			print("Percent Won: {:.5}%".format((games_won / games_played) * 100))

	def get_best_move(self) -> tuple:
		# Returns a tuple containing the cell with the lowest probability of containing a mine
		main_data = get_training_data(self.game, self.height, self.width)
		secondary_data = np.array([np.where(main_data[0] == 0, 1, 0)])

		prediction = self.model.predict([np.array([np.einsum("ijk->jki", main_data)]), np.array([np.einsum("ijk->jki", secondary_data)])])
		prediction = prediction[0]
		prediction = np.einsum("ijk->kij", prediction)
		prediction = prediction[0]

		lowest_probability = np.where((prediction + main_data[0]) == (prediction + main_data[0]).min())
		best_row = lowest_probability[0][0]
		best_column = lowest_probability[1][0]

		return best_row, best_column

if __name__ == "__main__":
	game = GameTable()
	solver = Solver(game)
	#solver.train(200, 100, 2)
	solver.test(100)
	solver.test_past_5_moves(100)