import tensorflow as tf
import numpy as np

from tensorflow.keras import layers, models
from table import GameTable

def create_model(height: int = 8, width: int = 8) -> models:
	# Creates the architecture for the model: use mode.summary() to visualize it.
	main_input_layer = layers.Input(shape = (height, width, 10))
	secondary_input_layer = layers.Input(shape = (height, width, 1))

	first_convolutional_layer = layers.Conv2D(64, (3,3), padding = "same", activation = "relu")(main_input_layer)
	second_convolutional_layer = layers.Conv2D(64, (3,3), padding = "same", activation = "relu")(first_convolutional_layer)
	third_convolutional_layer = layers.Conv2D(64, (3,3), padding = "same", activation = "relu")(second_convolutional_layer)
	fourth_convolutional_layer = layers.Conv2D(64, (3,3), padding = "same", activation = "relu")(third_convolutional_layer)
	fifth_convolutional_layer = layers.Conv2D(64, (3,3), padding = "same", activation = "relu")(fourth_convolutional_layer)
	sixth_convolutional_layer = layers.Conv2D(1, (1,1), padding = "same", activation = "sigmoid")(fifth_convolutional_layer)

	output_layer = layers.multiply([sixth_convolutional_layer, secondary_input_layer]) # by multiplying the last convolutional layer with the secondary input layer the discovered cells have a 0% probability of containing a mine
	model = models.Model(inputs = [main_input_layer, secondary_input_layer], outputs = output_layer)
	model.compile(optimizer = "adam", loss = "binary_crossentropy", metrics = ["accuracy"])

	#model.summary() # uncomment to see the architecture of the model
	return model

def load_model_from_file(model: models, height: int = 8, width: int = 8) -> models:
	# Loads the model from the "model.h5" file
	model = models.load_model("model.h5")
	return model

def get_training_data(game: GameTable, height: int = 8, width: int = 8) -> np.array:
	# Returns the needed training data:
	# We have 10 channels for the input data: a one-hot encoding of the cell's state.
	# training_data[0] shows if the cell is discovered or not
	# training_data[1-9] shows if the cell contains the number 1-9 or not
	training_data = np.zeros((10, height, width))

	for index_rows in range(game.rows):
		for index_columns in range(game.columns):
			value = game.table[index_rows][index_columns]
			if value != "_" and value != "F":
				training_data[0, index_rows, index_columns] = 1
			try:
				value = int(value)
				training_data[value + 1, index_rows, index_columns] = 1
			except Exception:
				pass

	return training_data