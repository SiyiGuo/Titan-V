import copy
import time

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
        
        mode = input()
        self.mode = mode

        return self.board, self.mode

"""Notation Area"""
EMPTY = "-"
BANNED = "X"
WHITE = "O"
BLACK = "@"

class Board(object):
    
    __directions = {
        "top": (-1,0),
        "bot": (1,0),
        "left": (0,-1),
        "right": (0,1)
    }

    __jumpDirections = {
        "top": (-2,0),
        "bot": (2,0),
        "left": (0,-2),
        "right": (0,2)
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
                #the case it should not mode
                print("fail"+str((x_dest, y_dest)+str((x_next, y_))))
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
        moves = set()

        for x in range(self.n):
            for y in range(self.n):
                if self.pieces[x][y] == color:
                    newMoves = self.getValidMoveForPiece((x,y))
                    moves.update(newMoves)
            
        return list(moves)

    def opposite(self,color):
        return{
            WHITE:BLACK,
            BLACK:WHITE,
            EMPTY:None,
            BANNED:None
        }[color]

    def executeMove(self, piecePosition, pieceDestination):    
        """
        make the move from orginal position to target position
        
        """ 
        x_orig, y_orig = piecePosition
        x_dest, y_dest = pieceDestination
        if self.pieces[x_orig][y_orig] == EMPTY:
            return

        self.pieces[x_dest][y_dest] = self.pieces[x_orig][y_orig]
        self.pieces[x_orig][y_orig] = EMPTY
        
        friend = self.pieces[x_dest][y_dest]
        enemy = self.opposite(self.pieces[x_dest][y_dest])

        for x_dir, y_dir in self.__directions.values():
            #if the piece 2 blocks away is the same color 
            #   and the piese next to current block is the opposite color 
            #eat it
            try:
                if self.pieces[x_dest + 2*x_dir][y_dest + 2*y_dir] == BANNED or self.pieces[x_dest + 2*x_dir][y_dest + 2*y_dir] == friend and self.pieces[x_dest + x_dir][y_dest + y_dir] == enemy:
                    self.pieces[x_dest + x_dir][y_dest + y_dir] = EMPTY
            except:
                continue

        for x_dir, y_dir in self.__directions.values():

            #if both diresctions are enemy
            #be eaten 
            try:
                if self.pieces[x_dest + x_dir][y_dest + y_dir] == BANNED or self.pieces[x_dest + x_dir][y_dest + y_dir] == enemy and self.pieces[x_dest - x_dir][y_dest - y_dir] == enemy:
                    self.pieces[x_dest][y_dest] = EMPTY
            except:
                continue
        
    def checkEat(self, piecePosition, pieceDestination):    
        """
        make the move from orginal position to target position
         
        """ 
        x_orig, y_orig = piecePosition 
        x_dest, y_dest = pieceDestination
        self.pieces[x_dest][y_dest] = self.pieces[x_orig][y_orig]
        self.pieces[x_orig][y_orig] = EMPTY
        friend = self.pieces[x_dest][y_dest]
        enemy = self.opposite(self.pieces[x_dest][y_dest])

class Masscare(object):
    def __init__(self, board):
        self.board = board
        enemys = []
        friends = []
        for x in range(len(self.board.pieces)):
            for y in range(len(self.board.pieces[x])):
                if self.board.pieces[x][y] == BLACK:
                    enemys.append((x,y))
                elif self.board.pieces[x][y] == WHITE:
                    friends.append((x,y))
        self.killBlacks(enemys, friends)
    
    def killBlacks(self, enemys, friends):
        i = 0
        while(len(enemys) != 0):
            if self.kill(enemys[i], friends):
                i = -1
                enemys = []
                for x in range(len(self.board.pieces)):
                    for y in range(len(self.board.pieces[x])):
                        if self.board.pieces[x][y] == BLACK:
                            enemys.append((x,y))
            i+=1
    
    def kill(self, location, friends):
        x_enemy, y_enemy = location
        closeFriends = self.closestFriend(location,friends)
        killPos = self.killPosition(location)
        for posPair in killPos:
            for pos in posPair:
                for friend in closeFriends:
                    if self.moveable(friend, pos):
                        self.move(friend, pos)
                        closeFriends.remove(friend)
                        break
                if self.board.pieces[x_enemy][y_enemy] == EMPTY:
                    return True
        return False
        
    def moveable(self,origLocation, destLocation):
        o_visited = []
        d_visited = []

        o_toVisit = []
        d_toVisit = []

        o_distance = 0
        d_distance = 0

        o_toVisit.append(origLocation)
        d_toVisit.append(destLocation)

        while (len(o_toVisit) > 0 and len(d_toVisit)> 0): 

            if d_distance < o_distance:
                loc = d_toVisit.pop(0)
                d_visited.append(loc)
                
                toVisit = self.board.getValidMoveForPiece(loc)
                for x in toVisit:
                    if x not in d_visited:
                        d_toVisit.append(x)
                d_distance += 1

            else:
                loc = o_toVisit.pop(0)
                o_visited.append(loc)
                toVisit = self.board.getValidMoveForPiece(loc)
                for x in toVisit:
                    if x not in o_visited:
                        o_toVisit.append(x)
                o_distance += 1

            for x in o_visited:
                if x in d_visited:
                    return True

        return False 
    
    def move(self,origLocation, destLocation):
        toVisit = [origLocation]
        shortestPath = {origLocation: [origLocation]}
        while destLocation not in shortestPath.keys():
            loc = toVisit.pop(0)
            
            for x in self.board.getValidMoveForPiece(loc):
                if x in shortestPath.keys():
                    if len(shortestPath[loc])+1 <= len(shortestPath[x]):
                        shortestPath[x] = shortestPath[loc]
                        shortestPath[x].append(x)
                else:
                    shortestPath[x] = copy.deepcopy(shortestPath[loc])
                    shortestPath[x].append(x)
                    toVisit.append(x)
        
        lastLoc = origLocation
        i = 0
        for path in shortestPath[destLocation]: 
            if i == 0:
                i+=1
                continue
            print(str(lastLoc) + "------>>" + str(path))
            self.board.executeMove(lastLoc,path)
            lastLoc = path


    def closestFriend(self, enemyLocation, friends):
        distances = {}
        for x in friends:
            distances[x] = self.distance(enemyLocation, x)
        distances = sorted(distances, reverse = True)
        return distances
        

    def distance(self, enenyLocation, myLocation):
        x_enemy, y_enemy = enenyLocation
        x_me, y_me = myLocation
        return ((x_enemy-x_me)**2 + (y_enemy-y_me)**2)        
    
    def killPosition(self, enemyLocation):
        __killDirections = {
            "vertical": (1,0),
            "horizontal": (0,1),
        }

        result = []
        x_enemy,y_enemy = enemyLocation

        for x_dir,y_dir in __killDirections.values():
            x1 = x_enemy + x_dir
            y1 = y_enemy + y_dir
            x2 = x_enemy - x_dir
            y2 = y_enemy - y_dir
            positions = []
            if x1 > 7 or y1 > 7 or self.board.pieces[x1][y1] == BLACK or self.board.pieces[x2][y2] == BLACK:
                continue
            if x1 < 8 and y1 < 8 and self.board.pieces[x1][y1] == EMPTY:
                positions.append((x1, y1))
            if self.board.pieces[x2][y2] == EMPTY:
                positions.append((x2, y2))
            result.append(positions)
        return result   
    
boardReader = BoardReader()
canoicalBoard, mode = boardReader.readInput()

board = Board(8, canoicalBoard)
if mode == "move":
    
    start = time.time()
    print(len(board.getAllLegalMoves(WHITE)))
    print(len(board.getAllLegalMoves(BLACK)))
    end = time.time()
    print(end)
    print(start)
else:
    mass = Masscare(board)
    print(mass.board.pieces)



