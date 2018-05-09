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
Coordinate represented as (x,y) = (row, column)
WHITE goes first
"""

"""
Notation Area
hacked to run first
"""
import numpy as np
EMPTY = 0
BANNED = 9
CORNER = 3
WHITE = 1
BLACK = -1

class Board(object):
    
    __directions = [(-1,0), (1,0), (0,-1), (0,1)]
        # "left": (0,-1),
        # "right": (0,1),
        # "top": (-1,0),
        # "bot": (1,0)

    __jumpDirections = [(-2,0), (2,0), (0,-2), (0,2)]
    # {
    #     "left": (0,-2),
    #     "right": (0,2),
    #     "top": (-2,0),
    #     "bot": (2,0)
    # }

    direction_combine = __directions + __jumpDirections

    def __init__(self, n, obBoard):
        """board setup"""
        """coordinate system: (row, column)"""
        self.n = n
        self.pieces = np.array(obBoard).reshape(8,8) # temporally hold for PUBgGame Function. Renew every time
    
    def _check_valid_jump(self, piecePosition, direction):
        """
        Given a jump direction
        return Valid, move
        """
        y_orig, x_orig = piecePosition

        y_dir, x_dir = direction # find the direction
        y_next, x_next = (y_orig + y_dir // 2, x_orig + x_dir // 2) # find the piece next to this piece
        
        y_dest, x_dest = (y_orig + y_dir,x_orig + x_dir)

        if (y_next < 8-self.n or x_next < 8-self.n or y_dest < 8-self.n or x_dest < 8-self.n) or (y_next >= self.n or x_next >= self.n or y_dest >= self.n or x_dest >= self.n):
            return False, None
        else:
            # check whether there is a piece next to it
            if self.pieces[y_next][x_next] == EMPTY or self.pieces[y_next][x_next] == BANNED or self.pieces[y_next][x_next] == CORNER:
                return False, None
            else:
                # the case white of black piece is next to it
                if self.pieces[y_dest][x_dest] == EMPTY:
                    return True, (y_dest, x_dest)
                else:
                    return False, None

    def _check_valid_move(self, piecePosition, direction):
        """
        check whether this direction if valid to move
        valid: True of False
        move: if valid return the destination
        """ 
        y_orig, x_orig = piecePosition
        y_dir, x_dir = direction
        y_dest, x_dest = (y_orig + y_dir,x_orig + x_dir)

        if (y_dest < 8-self.n or x_dest < 8-self.n) or (y_dest >= self.n or x_dest >= self.n):
            return False, None
        else:
            if self.pieces[y_dest][x_dest] == EMPTY:
                # empty place, can move
                return True, (y_dest, x_dest)
            else:
                # cover other case
                return False, None

    def getValidMoveForPiece(self,piecePosition):
        """
        take a piece's (col, row) coordinate,
        return a 1*8 vector
        [up down left right, upJump, downJump, leftJump, rightJump]
        """
        #conver to row, column
        (x,y) =piecePosition

        piecePosition = (y,x)

        
        moves = [0] * 8

        if self.pieces[y][x] != WHITE and self.pieces[y][x] != BLACK:
            return moves

        count = 0
        for direction in self.__directions:
            valid, move = self._check_valid_move(piecePosition, direction)
            if valid:
                moves[count] = 1
            count += 1
        
        for jumpDirection in self.__jumpDirections:
            valid,move = self._check_valid_jump(piecePosition, jumpDirection)
            if valid:
                moves[count] = 1
            count += 1

        return moves

    def opposite(self,color):
        """
        return the notation of opposite color
        """
        return{
            WHITE:BLACK,
            BLACK:WHITE,
            EMPTY:None,
            BANNED:None,
            CORNER:None
        }[color]

    def shrink(self, turn):
        # self.n will be
        # 8
        # 7
        # 6
        # set all banned area
        # print("Before shrink:\n%s"%self.pieces.reshape(8,8))
        self.pieces[8 - self.n] = BANNED
        self.pieces[self.n - 1] = BANNED
        self.pieces[:, 8-self.n] = BANNED
        self.pieces[:, self.n - 1] = BANNED

        # shringk dimension
        # 8 -> 7 1st call
        # 7 -> 6 2nd call
        self.n -= 1

        # Adding new corner
        # slowly set the top four corner, and take out pieces
        # Top left, bot let, bot right, top right
        top = 8 - self.n
        left = top
        bot = self.n - 1
        right = bot

        # Top Left
        self.pieces[top][left] = CORNER
        if self.opposite(self.pieces[top][left + 1]) == self.pieces[top][left+2]:
            self.pieces[top][left + 1] = EMPTY
        if self.opposite(self.pieces[top+1][left]) == self.pieces[top+2][left]:
            self.pieces[top+1][left] = EMPTY

        # Bot Left
        self.pieces[bot][left] = CORNER

        if self.opposite(self.pieces[bot - 1][left]) == self.pieces[bot - 2][left]:
            self.pieces[bot - 1][left] = EMPTY
        if self.opposite(self.pieces[bot][left+1]) == self.pieces[bot][left+2]:
            self.pieces[bot][left+1] = EMPTY
        
        # Bot right
        self.pieces[bot][right] = CORNER
        if self.opposite(self.pieces[bot-1][right]) == self.pieces[bot - 2][right]:
            self.pieces[bot-1][right] = EMPTY
        if self.opposite(self.pieces[bot][right-1]) == self.pieces[bot][right-2]:
            self.pieces[bot][right-1] = EMPTY

        # Top right
        self.pieces[top][right] = CORNER
        if self.opposite(self.pieces[top+1][right]) == self.pieces[top+2][right]:
            self.pieces[top+1][right] = EMPTY
        if self.opposite(self.pieces[top][right-1]) == self.pieces[top][right-2]:
            self.pieces[top][right-1] = EMPTY

        # print("Shringk at turn:%s, top:%s, bot:%s, after self.n -= 1:%s, board:\n%s"%(turn, top, bot, self.n, np.array(self.pieces).reshape(8,8)))

    def executeMove(self, piecePosition, pieceDestination):    
        """
        in the form: (column, row)
        """ 
        # (column, row) -> (row, column)
        x_orig, y_orig = piecePosition
        x_dest, y_dest = pieceDestination

        if self.pieces[y_dest][x_dest] == EMPTY:
            self.pieces[y_dest][x_dest] = self.pieces[y_orig][x_orig]
            self.pieces[y_orig][x_orig] = EMPTY
            
            #Checking the eat now
            friend = self.pieces[y_dest][x_dest]
            # print("Friend:%s, place:%s"%(friend, self.pieces[y_dest][x_dest]))
            enemy = self.opposite(self.pieces[y_dest][x_dest])
            # print("Enemy:%s, place:%s"%(enemy, self.pieces[y_dest][x_dest]))

            for direction in self.__directions:
                y_dir, x_dir = direction

                #Case: Friend Enemy Friend
                #then Enemy will be Eat
                a = y_dest + 2*y_dir
                b = x_dest + 2*x_dir
                c = y_dest + y_dir
                d = x_dest + x_dir
                if  (a < 0 or b < 0 or c < 0 or d < 0) or (a >= self.n or b >= self.n or c >= self.n or d >= self.n):
                    continue
                elif (self.pieces[a][b] == friend or self.pieces[a][b] == CORNER) and self.pieces[c][d] == enemy:
                    self.pieces[c][d] = EMPTY

            for direction in self.__directions:
                y_dir, x_dir = direction

                #Case: Enemy Friend Enemy
                #i am eaten
                a = y_dest + y_dir
                b = x_dest + x_dir
                c = y_dest - y_dir
                d = x_dest - x_dir

                if  (a < 0 or b < 0 or c < 0 or d < 0) or (a >= self.n or b >= self.n or c >= self.n or d >= self.n):
                    continue
                elif (self.pieces[a][b] == enemy or self.pieces[a][b] == CORNER) and (self.pieces[c][d] == enemy or self.pieces[c][d] == CORNER):
                    self.pieces[y_dest][x_dest] = EMPTY

    def countPieces(self):
        whiteCount, blackCount = 0,0
        for x in range(self.n):
            for y in range(self.n):
                if self.pieces[x][y] == WHITE:
                    whiteCount += 1
                elif self.pieces[x][y] == BLACK:
                    blackCount += 1

        #rmove 2 as they are corner piece
        return (blackCount, whiteCount)


