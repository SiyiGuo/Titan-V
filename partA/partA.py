class BoardReader(object):
    def __init__(self):
        self.board = [] # a two dimension list
        self.mode = ""

    def processLine(self,line):
        """reserved for future modification"""
        return line

    def readInput(self):
        for i in range(8):
            line = input().split(" ")
            self.board.append(self.processLine(line))
        
        print(self.board)

        mode = input()
        self.mode = mode

        return self.mode, self.board

class Board(object):
    
    __directions = {
        "top": (-1,0)
        "bot": (1,0)
        "left": (0,-1)
        "right": (0,1)
    }

    """Notation Area"""
    EMPTY = "-"
    BANNED = "X"
    WHITE = "O"
    BLACK = "@"
    def __intit__(self,n, canonicalBoard = None):
        """board setup"""
        """coordinate system: (row, column)"""

        self.n = n
        if canoicalBoard is not None:
            self.pieces = [[EMPTY]*self.n]*self.n
            self.pieces[0][0] = BANNED #top left 
            self.pieces[0][self.n] = BANNED #top right
            self.pieces[self.n - 1][0] = BANNED #bottom left
            self.pieces[self.n - 1][self.n - 1] = BANNED #bottom right corner
        else:
            self.pieces = canonicalBoard
    
    def _check_valid_move(self, piecePosition, direction):
        """
        check whether this direction if valid to move
        valid: True of False
        move: if valid return the destination
        """
        x_orig, y_orig = piecePosition
        x_dir, y_dir = direction
        x_dest, y_dest = (x_orig + x_dir,y_orig + y_dir)

        if x_dest < 0 or x_dest > self.n:
            return False, None
        else if y_dest < 0 or y_dest > self.n:
            return False, None
        else if self.pieces[x_dest][y_dest] is BANNED:
            return False, None
        else if self.pieces[x_dest][y_dest] is EMPTY:
            # empty place, can move
            return True, (x_dest, y_dest)
        else if self.pieces[x_dest][y_dest] == self.pieces[x_orig][y_orig]:
            #if destination is the same piece

            #TODO: see if we can make a jump
            return False, None

        else if self.pieces[x_dest][y_dest] != self.pieces[x_orig][y_orig]:
            #if destination is not the same piece

            #TODO: see if we can make a jump
            return False, None


        #now it is the valid case
        return True, (x_dest, y_dest)



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
            valid, move = self._check_valid_move(piecePosition, direction):
            if valid:
                moves.append(move)
        
        return moves
    
    def getAllLegalMoves(self, color):
        """
        Given a color, return all the legal moves
        """



    
    


boardReader = BoardReader()
canoicalBoard, mode = boardReader.readInput()

board = Board(canoicalBoard)




