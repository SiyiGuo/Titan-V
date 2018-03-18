"""
Coordinate system:
 0 1 2 3 4 5 6 7 x
0
1
2
3
4
5
6
7
y
Coordinate represented as (x,y) = (column, row)
WHITE goes first
"""

"""
Notation Area
hacked to run first
"""
EMPTY = 0
BANNED = 9
WHITE = 1
BLACK = -1

class Board(object):
    
    __directions = {
        "left": (-1,0),
        "right": (1,0),
        "top": (0,-1),
        "bot": (0,1)
    }

    __jumpDirections = {
        "left": (-2,0),
        "right": (2,0),
        "top": (0,-2),
        "bot": (0,2)
    }

    def __init__(self, n, canonicalBoard = None):
        """board setup"""
        """coordinate system: (row, column)"""

        self.n = n
        if canoicalBoard is None:
            self.pieces = [[EMPTY]*self.n]*self.n
            self.pieces[0][0] = BANNED #top left 
            self.pieces[0][self.n - 1] = BANNED #top right
            self.pieces[self.n - 2][0] = BANNED #bottom left
            self.pieces[self.n - 2][self.n - 2] = BANNED #bottom right corner
        else:
            self.pieces = canonicalBoard
    
    def _check_valid_jump(self, piecePosition, direction):
        """
        Given a jump direction
        return Valid, move
        """
        x_orig, y_orig = piecePosition

        x_dir, y_dir = direction #find the direction
        x_next, y_next = (x_orig + x_dir // 2, y_orig + y_dir // 2) #find the piece next to this piece
        
        x_dest, y_dest = (x_orig + x_dir,y_orig + y_dir)
        try:
            #check whether there is a piece next to it
            if self.pieces[x_next][y_next] is EMPTY or self.pieces[x_next][y_next] is BANNED:
                return False, None
            else:
                #the case white of black piece is next to it
                if self.pieces[x_dest][y_dest] is EMPTY:
                    return True, (x_dest, y_dest)
                else:
                    return False, None
        except:
            #cover the case index out of range
            return False, None

    def _check_valid_move(self, piecePosition, direction):
        """
        check whether this direction if valid to move
        valid: True of False
        move: if valid return the destination
        """ 
        x_orig, y_orig = piecePosition
        x_dir, y_dir = direction
        x_dest, y_dest = (x_orig + x_dir,y_orig + y_dir)

        try:
            if self.pieces[x_dest][y_dest] is EMPTY:
                # empty place, can move
                return True, (x_dest, y_dest)
            else:
                #cover other case
                return False, None
        except:
            #cover the case index out of range
            return False, None

    def getValidMoveForPiece(self,piecePosition):
        """
        take a piece's (row, col) coordinate,
        return all valid move around this pieces
        """
        (x,y) =piecePosition

        if self.pieces[x][y] is EMPTY:
            """this is an empty piece, skip"""
            return None

        # to be returned
        moves = []
        for direction in self.__directions.values():
            valid, move = self._check_valid_move(piecePosition, direction)
            if valid:
                moves.append(move)
        
        for jumpDirection in self.__jumpDirections.values():
            valid,move = self._check_valid_jump(piecePosition, jumpDirection)
            if valid:
                moves.append(move)
        
        return moves
    
    def getAllLegalMoves(self, color):
        """
        Given a color, return all the legal moves
        """
        moves = []

        for x in range(self.n):
            for y in range(self.n):
                if self.pieces[x][y] == color:
                    newMoves = self.getValidMoveForPiece((x,y))
                    moves += newMoves
            
        return moves

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

    def executeMove(self, piecePosition, pieceDestination):    
        """
        Perform moving on the board
        Eat enemy pieces as necessary
        """ 
        x_orig, y_orig = piecePosition
        x_dest, y_dest = pieceDestination
        if self.pieces[x_orig][y_orig] == EMPTY:
            self.pieces[x_dest][y_dest] = self.pieces[x_orig][y_orig]
            self.pieces[x_orig][y_orig] = EMPTY
        
        #Checking the eat now
        friend = self.pieces[x_dest][y_dest]
        enemy = self.opposite(self.pieces[x_dest][y_dest])

        for direction in self.__directions.values():
            x_dir, y_dir = direction

            #case Friend Enemy Friend
            #then Enemy will be Eat
            if self.pieces[x_dest + 2*x_dir][y_dest + 2*y_dir] == friend and self.pieces[x_dest + x_dir][y_dest + y_dir] == enemy:
                self.pieces[x_dest + x_dir][y_dest + y_dir] = EMPTY

        for direction in self.__directions.values():
            x_dir, y_dir = direction

            #ase Enemy Friend Enemy
            #i am eaten
            if self.pieces[x_dest + x_dir][y_dest + y_dir] == enemy and self.pieces[x_dest - x_dir][y_dest - y_dir] == enemy:
                self.pieces[x_dest][y_dest] = EMPTY

    def countPieces(self):
        """
        input:
            the color which you want to count pieces
        return:
            {"black"}
        """
        whiteCount, blackCount = 0,0
        for x in range(self.n):
            for y in range(self.n):
                if self.pieces[x][y] == WHITE:
                    whiteCount += 1
                elif self.pieces[x][y] == BLACK:
                    blackCount += 1

        return (blackCount, whiteCount)


