"""
Board data:
    1=white, -1=black, =00empty
    (x,y) = (column, row)
Note:
    this version of code has not adding
    the BANNED area
"""

"""
Notation Area
hacked to run first
"""
EMPTY = 0
BANNED = 9
WHITE = 1
BLACK = -1
class Board():

    # list of all 8 directions on the board, as (x,y) offsets
    __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

    def __init__(self, n):
        "Set up initial board configuration."

        self.n = n
        # Create the empty board array.
        self.pieces = [None]*self.n
        for i in range(self.n):
            self.pieces[i] = [0]*self.n

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def countDiff(self, color):
        """Counts the # pieces of the given color
        (1 for white, -1 for black, 0 for empty spaces)"""
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==color:
                    count += 1
                if self[x][y]==-color:
                    count -= 1
        return count

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black)
        """
        moves = set()  # stores the legal moves.

        # Get all the squares with pieces of the given color.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y]==EMPTY:
                    moves.update((x,y))
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
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=white,-1=black)
        """

        x, y = move
        self.pieces[x][y] = color

        #Checking the eat now
        friend = color
        enemy = self.opposite(friend)

        #process the eat of enemy first according to the rult
        for direction in self.__directions.values():
            x_dir, y_dir = direction

            #case Friend Enemy Friend
            #then Enemy will be Eat
            if self.pieces[x + 2*x_dir][y + 2*y_dir] == friend and self.pieces[x + x_dir][y + y_dir] == enemy:
                self.pieces[x + x_dir][y + y_dir] = EMPTY

        #process myself then
        for direction in self.__directions.values():
            x_dir, y_dir = direction

            #ase Enemy Friend Enemy
            #i am eaten
            if self.pieces[x_dest + x_dir][y_dest + y_dir] == enemy and self.pieces[x_dest - x_dir][y_dest - y_dir] == enemy:
                self.pieces[x_dest][y_dest] = EMPTY



