import time
from solver import Solver

class Controller(object):
	def __init__(self, solver: Solver) -> None:
		self.solver = solver

	def play(self) -> None:
		# Plays a game from the beggining to the end until the user is satisfied
		print("Golden rule: ALWAYS keep the minesweeper window visible. ALWAYS. You have been warned!")
		print("Wanna see a master at work huh? Fine, let's go!")
		print("Choose the time between the moves (in seconds, obviously): ")
		time_between_moves = float(input())
		while True:
			outcome = "win"
			
			self.solver.game.restart_game()
			self.solver.game.left_click(self.solver.width // 2, self.solver.height // 2)
			time.sleep(time_between_moves)
			if self.solver.game.game_lost():
				print("Oh come on, what are the odds?!")
				outcome = "lose"

			while self.solver.game.game_over() == False:
				row, column = self.solver.get_best_move()
				self.solver.game.left_click(column, row)
				time.sleep(time_between_moves)

			if self.solver.game.game_won():
				print("Easy win, see?")
			else:
				print("Uhm... You certainly did something wrong, let me have another go!")
				outcome = "lose"

			if outcome == "lose":
				print("Give me another chance at redemption?")
			else:
				print("See me triumph again?")

			print("y/n")
			answer = input()
			if answer == "n":
				print("Fine... your loss...")
				time.sleep(time_between_moves)
				break
			else:
				print("That's what I wanna hear!")
				time.sleep(time_between_moves)

	def solve(self) -> None:
		# Finishes an already ongoing game
		print("Golden rule: ALWAYS keep the minesweeper window visible. ALWAYS. You have been warned!")
		print("Too hard for you? Good thing I'm here. Let's go")
		print("Choose the time between the moves (in seconds, obviously): ")
		time_between_moves = float(input())
		
		while self.solver.game.game_over() == False:
			row, column = self.solver.get_best_move()
			self.solver.game.left_click(column, row)
			time.sleep(time_between_moves)

		if self.solver.game.game_won():
			print("Done... anything else you need me to solve for you?..")
		else:
			print("Your previous moves were just too awful, couldn't recover from that.")