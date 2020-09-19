from table import GameTable
from controller import Controller
from solver import Solver

def run() -> None:
	game = GameTable()
	solver = Solver(game)
	controller = Controller(solver)

	print("Please choose an option from below")
	print("1. See the solver play a game from beggining to end.")
	print("2. See the solver finish an ongoing game.")
	action = int(input())
	if action == 1:
		controller.play()
	elif action == 2:
		controller.solve()
	else:
		print("The only options are 1 or 2. Please choose accordingly!")

if __name__ == "__main__":
	run()