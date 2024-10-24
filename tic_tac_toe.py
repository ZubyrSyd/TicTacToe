"""A tic-tac-toe game built with Python and Tkinter."""


import tkinter as tk
from tkinter import font
from typing import NamedTuple
from itertools import cycle

class Player(NamedTuple): #player class where label stores the signs x and o, and color attribute holds current player position on game board
    label: str
    color: str

class Move(NamedTuple): #move class where row and col holds coordinates for the move's target cell, label is blank since specific move hasn't been made yet
    row: int
    col: int
    label: str = ""


BOARD_SIZE = 3 #holds size of tic tac toe game
DEFAULT_PLAYERS = ( #defines a 2 item tuple representing each player in the game
    Player(label="X", color="blue"),
    Player(label="O", color="green"),
) 

class TicTacToeGame:
    #Adjusting all settings regarding logic for the game
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE): #players hold a tuple of 2 player objects rep. X and O, board_size holds the size of the game board 
        self._players = cycle(players) #cyclical interator over input tuple of players
        self.board_size = board_size #size of the game board
        self.current_player = next(self._players) #the current player
        self.winner_combo = [] #Combination of cells that defines the winner
        self._current_moves = [] #list of players moves in a given game
        self._has_winner = False #Determines if the game has a winner or not
        self._winning_combos = [] #list defining cell combinations that define a win
        self._setup_board()

    def _setup_board(self): #initial list of values for current moves. Creates a list of lists that contains the coordinates of containing cell and player's label
        self._current_moves = [
            [Move(row,col) for col in range(self.board_size)] 
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def process_move(self, move): #Process the current move and checks if it's a win.
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    
    def has_winner(self):
        """Return true if the game has a winner,and false otherwise."""
        return self._has_winner

    def _get_winning_combos(self):
        rows = [ #row attribute holds a list of 3 sublists, in which each sublist represents a row on the grid and have 3 move objects in it
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)] #gets coordinates of each cell in columns
        first_diagonal = [row[i] for i, row in enumerate(rows)] #gets coordinates of each cell diag.
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))] #gets coordinates of each cell diag.
        return rows + columns + [first_diagonal, second_diagonal] #returns a list of lists containing all possible winning combinations

    def is_valid_move(self, move): #Validates eveyr player's move to ensure there's no winner, and the selected move hasn't already been played yet
        """Return True if move is valid, and False otherwise."""
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def toggle_player(self):
        """Return a toggled player."""
        self.current_player = next(self._players)

    def is_tied(self):
        """Return True if the game is tied, and False otherwise."""
        no_winner = not self._has_winner #checks if theres no winner yet
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves) #if both are true, then game tied


    def reset_game(self):
        """Reset the game state to play again."""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []


   
class TicTacToeBoard(tk.Tk):

    def __init__(self, game): #gives full access to the game logic from the game board
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._cells = {}
        self._game = game
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Play Again", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color
        
    
    def _create_board_display(self): #game display
        display_frame = tk.Frame(master=self) #frame object
        display_frame.pack(fill=tk.X) #places frame object on the main window's top border
        self.display = tk.Label( #label object placed inside frame that has text and font size adjusted
            master=display_frame,
            text="Ready?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack() #displays label inside the frame

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self) #frame object to hold game's grid of cells
        grid_frame.pack() #frame occupies from under game display to bottom of the window
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight = 1, minsize = 50) #configures cell size
            self.columnconfigure(row, weight=1, minsize = 75) #configures cell size
            for col in range(self._game.board_size): #loops over 3 column coordinates
                button = tk.Button( #defines button object for every cell in grid
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col) #adds every button to the cells dictionary
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def play(self, event):
        """Handle a player's move."""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg="Tied game!", color="red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Player "{self._game.current_player.label}" won!'
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s turn"
                self._update_display(msg)

    def reset_board(self):
        """Reset the game's board to play again."""
        self._game.reset_game()
        self._update_display(msg="Ready?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")
    
        

def main():
    """Create the game's board and run its main loop."""
    game = TicTacToeGame() #instance, which is used to handle game logic
    board = TicTacToeBoard(game) #instance, which injects game logic into the game board
    board.mainloop()

if __name__ == "__main__": #controls the execution of the code
    main()
        
        

