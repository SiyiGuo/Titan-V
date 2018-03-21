"""
Board data:
    1=white, -1=black, =00empty
    (x,y) = (column, row)
Note:
    this version of code has not adding
    the BANNED area
"""

import numpy as np

"""
Notation Area
hacked to run first
"""
EMPTY = 0
BANNED = 0
WHITE = 1
BLACK = -1
class Board():

    # direction: (row, column)
    __directions = {
        "top": (-1,0),
        "bot": (1,0),
        "left": (0,-1),
        "right": (0,1)
    }

    def __init__(self, n):
        """
        Set up initial board configuration.
        input: (column, row)
        middly process: (row, column)
        output:(column, row)
        """

        self.n = n
        # Create the empty board array.
        self.pieces = np.zeros((self.n, self.n))

        self.pieces[0][0] = BLACK
        self.pieces[0][self.n - 1] = BLACK
        self.pieces[self.n - 1][0] = WHITE
        self.pieces[self.n-1][self.n-1] = WHITE


    def countDiff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self.pieces[x][y]==color:
                    count += 1
                if self.pieces[x][y]==-color:
                    count -= 1
        return count

    def get_legal_moves(self, color):
        """
        Returns all the legal moves for the given color.
        (1 for white, -1 for black)
        output in the form (column, row)
        """
        moves = set()  # stores the legal moves.

        # Get all the squares with pieces of the given color.
        if color == BLACK:
            for y in range(2, self.n):
                for x in range(self.n):
                    if self.pieces[y][x]==EMPTY:
                        moves.update([(x,y)])
        elif color == WHITE:
            for y in range(self.n - 2):
                for x in range(self.n):
                    if self.pieces[y][x]==EMPTY:
                        moves.update([(x,y)])
        
        return list(moves)
            
    def opposite(self,color):
        """
        return the notation of opposite color
        """
        return{
            WHITE:BLACK,
            BLACK:WHITE,
            EMPTY:None,
            BANNED:None
        }[color]

    def execute_move(self, move, color):
        """
        Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=white,-1=black)
        input: 
            (column, row) = (x,y)
        process: 
            (row, column) = (y,x)
        """

        (x, y) = move #(column, row) from input
        self.pieces[y][x] = color

        #Checking the eat now
        friend = color
        enemy = self.opposite(friend)

        #process the eat of enemy first according to the rult
        for direction in self.__directions.values():
            y_dir, x_dir = direction

            #case Friend Enemy Friend
            #then Enemy will be Eat
            index_check = np.array([y + 2*y_dir, x + 2*x_dir, y + y_dir, x + x_dir])

            #as valid index are [0,......self.n-1] eg: n =8, n - 1 = 7, [0,....7]
            if (index_check < 0).any() or (index_check >= self.n).any():
                pass
            else:
                if np.array_equal(
                    [self.pieces[y + 2*y_dir][x + 2*x_dir],self.pieces[y + y_dir][x + x_dir]]
                    ,
                    [friend, enemy]
                    ):
                    self.pieces[y + y_dir][x + x_dir] = EMPTY

        #process myself then
        for direction in self.__directions.values():
            y_dir, x_dir = direction

            #ase Enemy Friend Enemy
            #i am eaten
            index_check = np.array([y + y_dir, x + x_dir, y - y_dir, x - x_dir])
            
            if (index_check < 0).any() or (index_check >= self.n).any():
                pass
            else:
                if np.array_equal(
                    [self.pieces[y+ y_dir][x + x_dir], self.pieces[y - y_dir][x - x_dir]]
                    ,
                    [enemy, enemy]
                    ):
                    self.pieces[y][x] = EMPTY



