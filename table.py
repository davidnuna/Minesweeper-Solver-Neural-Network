import win32gui
import win32api
import win32con
import mss

class GameTable(object):
	SQUARE_WIDTH = 16
	SQUARE_HEIGHT = 16
	IGNORED_PIXELS_X = 12
	IGNORED_PIXELS_Y = 55
	NUMBERS = {
	(192, 192, 192): 0,
	(0, 0, 255)    : 1,
	(0, 128, 0)    : 2,
	(255, 0, 0)    : 3,
	(0, 0, 128)    : 4,
	(128, 0, 0)    : 5,
	(0, 128, 128)  : 6,
	(0, 0, 0)      : 7,
	(128, 128, 128): 8}
	GREY = (192, 192, 192)
	DARK_GREY = (128, 128, 128)
	WHITE = (255, 255, 255)
	RED = (255, 0, 0)
	BLACK = (0, 0, 0)

	def __init__(self) -> None:
		self.table = [] 

		ms_window = win32gui.FindWindow(None, "Minesweeper X")
		if ms_window == 0:
			raise Exception("Minesweeper window not found!")

		ms_left, ms_top, ms_right, ms_bottom = win32gui.GetClientRect(ms_window)
		left, top = win32gui.ClientToScreen(ms_window, (ms_left, ms_top))
		right, bottom = win32gui.ClientToScreen(ms_window, (ms_right, ms_bottom))

		self.ms_dimensions = dict(top = top, left = left, width = right - left, height = bottom - top)
		self.sct = mss.mss()

		self.image_table = self.sct.grab(self.ms_dimensions)
			
		self.columns = (self.ms_dimensions["width"] - 2 * GameTable.IGNORED_PIXELS_X) // GameTable.SQUARE_WIDTH
		self.rows = (self.ms_dimensions["height"] - GameTable.IGNORED_PIXELS_Y - GameTable.IGNORED_PIXELS_X) // GameTable.SQUARE_HEIGHT

		for index_rows in range(self.rows):
			self.table.append([])
			for index_columns in range(self.columns):
				self.table[index_rows].append("_")

	def update(self) -> None:
		# The symbols are the following:
		# "_" -> undiscovered cell
		# "0-8" -> cell with a number in it
		# "F" -> cell with a flag in it
		# "M" -> cell with mine in it
		# "W" -> cell wrongly flagged (there was no mine in it)
		# "H" -> cell hit by player, the one with a mine in it (the one that made him lose)
		# Use the method "print_game" to visualize such a game state
		self.image_table = self.sct.grab(self.ms_dimensions)
		for index_rows in range(self.rows):
			for index_columns in range(self.columns):
				previously_changed = False
				middle_pixel_color = self.image_table.pixel((index_columns + 1) * GameTable.SQUARE_WIDTH + GameTable.IGNORED_PIXELS_X - 8, (index_rows + 1) * GameTable.SQUARE_HEIGHT + GameTable.IGNORED_PIXELS_Y - 8)
					
				if middle_pixel_color == GameTable.GREY: # check for free square
					down_pixel = self.image_table.pixel((index_columns + 1) * GameTable.SQUARE_WIDTH + GameTable.IGNORED_PIXELS_X - 1, (index_rows + 1) * GameTable.SQUARE_HEIGHT + GameTable.IGNORED_PIXELS_Y - 1)
					if down_pixel == GameTable.DARK_GREY: # it's a free square
						self.table[index_rows][index_columns] = "_"
						previously_changed = True
				if middle_pixel_color == GameTable.BLACK: # check for bomb and for flag
					upper_pixel = self.image_table.pixel((index_columns + 1) * GameTable.SQUARE_WIDTH + GameTable.IGNORED_PIXELS_X - 10, (index_rows + 1) * GameTable.SQUARE_HEIGHT + GameTable.IGNORED_PIXELS_Y - 10)
					if upper_pixel == GameTable.WHITE: # it's a bomb
						leftPixel = self.image_table.pixel((index_columns + 1) * GameTable.SQUARE_WIDTH + GameTable.IGNORED_PIXELS_X - 1, (index_rows + 1) * GameTable.SQUARE_HEIGHT + GameTable.IGNORED_PIXELS_Y - 8)
						if leftPixel == GameTable.RED:
							self.table[index_rows][index_columns] = "H"
						else:
							self.table[index_rows][index_columns] = "M"
						previously_changed = True
					if upper_pixel == GameTable.RED: # it's a flag
						self.table[index_rows][index_columns] = "F"
						previously_changed = True
	
				if middle_pixel_color == GameTable.RED: # check for wrong bomb flagged
					leftPixel = self.image_table.pixel((index_columns + 1) * GameTable.SQUARE_WIDTH + GameTable.IGNORED_PIXELS_X - 6, (index_rows + 1) * GameTable.SQUARE_HEIGHT + GameTable.IGNORED_PIXELS_Y - 8)
					if leftPixel == GameTable.BLACK:
						self.table[index_rows][index_columns] = "W"
						previously_changed = True

				if previously_changed == False:
					try:
						self.table[index_rows][index_columns] = str(GameTable.NUMBERS[middle_pixel_color])
					except KeyError:
						print("The Minesweeper window must be visible at all times!")
						exit()

	def left_click(self, coordinate_x: int, coordinate_y: int) -> None:
		# Left clicks the cell on the board with the given coordinates (discoveres it)
		if coordinate_x < 0 or coordinate_x >= self.columns or coordinate_y < 0 or coordinate_y >= self.rows:
			raise Exception("Invalid coordinates!")
		global_x = self.ms_dimensions["left"] + (coordinate_x + 1) * GameTable.SQUARE_WIDTH + GameTable.IGNORED_PIXELS_X - 8
		global_y = self.ms_dimensions["top"] + (coordinate_y + 1) * GameTable.SQUARE_HEIGHT + GameTable.IGNORED_PIXELS_Y - 8
		win32api.SetCursorPos((global_x, global_y))

		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, global_x, global_y, 0, 0)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, global_x, global_y, 0, 0)
		self.update()

	def right_click(self, coordinate_x: int, coordinate_y: int) -> None:
		# Right clicks the cell on the board with the given coordinates (flags it)
		if coordinate_x < 0 or coordinate_x >= self.columns or coordinate_y < 0 or coordinate_y >= self.rows:
			raise Exception("Invalid coordinates!")
		global_x = self.ms_dimensions["left"] + (coordinate_x + 1) * GameTable.SQUARE_WIDTH + GameTable.IGNORED_PIXELS_X - 8
		global_x = self.ms_dimensions["top"] + (coordinate_y + 1) * GameTable.SQUARE_HEIGHT + GameTable.IGNORED_PIXELS_Y - 8
		win32api.SetCursorPos((global_x, global_y))

		win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, global_x, global_y, 0, 0)
		win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, global_x, global_y, 0, 0)
		self.update()

	def restart_game(self) -> None:
		# Restarts the game by pressing the smiley button in the top side
		global_x = self.ms_dimensions["left"] + self.ms_dimensions["width"] // 2
		global_y = self.ms_dimensions["top"] + 20

		win32api.SetCursorPos((global_x, global_y))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, global_x, global_y, 0, 0)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, global_x, global_y, 0, 0)
		self.update()

	def game_lost(self) -> bool:
		# Checks if the game has been lost
		for index_rows in range(self.rows):
			if "H" in self.table[index_rows]:
				return True
		return False

	def game_won(self) -> bool:
		# Checks if the game has been won
		for index_rows in range(self.rows):
			for index_columns in range(self.rows):
				if self.table[index_rows][index_columns] == "_": 
					return False
		return True

	def game_over(self) -> bool:
		# Checks if the game has ended
		if self.game_lost() or self.game_won():
			return True
		return False

	def print_game(self) -> bool:
		# Prints the current state of the board
		for index_rows in range(self.rows):
			for index_columns in range(self.columns):
				print(self.table[index_rows][index_columns], end=" ")
			print()