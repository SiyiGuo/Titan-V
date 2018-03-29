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
        if x_dest in range(self.n) and y_dest in range(self.n) and x_next in range(self.n) and y_next in range(self.n):
            #check whether there is a piece next to it
            if self.pieces[x_next][y_next] is EMPTY or self.pieces[x_next][y_next] is BANNED:
                #the case it should not mode
                
                return False, None
            else:
                #the case white of black piece is next to it
                if self.pieces[x_dest][y_dest] is EMPTY:
                    return True, (x_dest, y_dest)
                else:
                    return False, None
        else:
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

        if x_dest in range(self.n) and y_dest in range(self.n):
            if self.pieces[x_dest][y_dest] is EMPTY:
                # empty place, can move
                return True, (x_dest, y_dest)
            else:
                #cover other case
                return False, None
        else:
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

        #return if piece position is empty
        if self.pieces[x_orig][y_orig] == EMPTY:
            return

        #make the move
        self.pieces[x_dest][y_dest] = self.pieces[x_orig][y_orig]
        self.pieces[x_orig][y_orig] = EMPTY
        
        friend = self.pieces[x_dest][y_dest]
        enemy = self.opposite(self.pieces[x_dest][y_dest])

        for x_dir, y_dir in self.__directions.values():
            #if the piece 2 blocks away is the same color 
            #   and the piese next to current block is the opposite color 
            #eat it
            
            try:
                p1 = self.pieces[x_dest + 2*x_dir][y_dest + 2*y_dir]
                p2 = self.pieces[x_dest + x_dir][y_dest + y_dir]
                if (p1 == BANNED or p1 == friend) and p2 == enemy:
                    self.pieces[x_dest + x_dir][y_dest + y_dir] = EMPTY
            except:
                continue

        for x_dir, y_dir in self.__directions.values():

            #if both diresctions are enemy
            #be eaten 
            
            try:
                p1 = self.pieces[x_dest + x_dir][y_dest + y_dir]
                p2 = self.pieces[x_dest - x_dir][y_dest - y_dir]
                if (p1 == BANNED or p1 == enemy) and (p2 == BANNED or p2 == enemy):
                    self.pieces[x_dest][y_dest] = EMPTY
            except:
                continue
        
    def checkEaten(self, pieceDestination):     
        """ 
        check if moving to this position will result in be eaten 
          
        """  
        x_dest, y_dest = pieceDestination

        enemy = BLACK

        for x_dir, y_dir in self.__directions.values():

            #if both directions are enemy/banned return true
            try:

                p1 = self.pieces[x_dest + x_dir][y_dest + y_dir]
                p2 = self.pieces[x_dest - x_dir][y_dest - y_dir]

                if (p1 == BANNED or p1 == enemy) and (p2 == BANNED or p2 == enemy):
                    return True

            except:
                continue

        return False

        

class Masscare(object):
    totalMove = 0
    def __init__(self, board):
        """ 
        find positions of enemies and friends
        excute killBlacks
          
        """  
        self.board = board
        enemys = []
        friends = []
        
        #record location of white and black pieces
        for x in range(len(self.board.pieces)):
            for y in range(len(self.board.pieces[x])):

                if self.board.pieces[x][y] == BLACK:
                    enemys.append((x,y))
                elif self.board.pieces[x][y] == WHITE:
                    friends.append((x,y))
        
        #kill all enemies
        self.killBlacks(enemys, friends)
    
    def killBlacks(self, enemys, friends):
        """ 
        kill all black pieces recorded
          
        """  
        while(enemys != []): #while there is still enemy
            for index, x in enumerate(enemys): #for every enemy

                if self.kill(x, friends):# kill this enemy if killable
                    
                    #refresh the pieces positions stored
                    enemys = []
                    friends = []
                    for x in range(len(self.board.pieces)):
                        for y in range(len(self.board.pieces[x])):
                            if self.board.pieces[x][y] == BLACK:
                                enemys.append((x,y))
                            elif self.board.pieces[x][y] == WHITE:
                                friends.append((x,y))
                    break
    
    def kill(self, location, friends):
        """ 
        return true if successfully kill the black piece on the location 
        reutrn false if fail  
        """  
        x_enemy, y_enemy = location
        closeFriends = self.closestFriend(location,friends) # return a list of friends in the order of distance
        killPos = self.killPosition(location) #get the positions required to fill to kill the black piece

        #try to fill those positions
        for posPair in killPos:
            for pos in posPair:
                for friend in closeFriends:

                    if self.moveable(friend, pos):#if moveable, move to that position
                        self.move(friend, pos)
                        closeFriends.remove(friend)
                        break

                if self.board.pieces[x_enemy][y_enemy] == EMPTY:#if black piece is eaten, reutrn true
                    return True

        return False
        
    def moveable(self,origLocation, destLocation):
        """ 
        if there is a path from origLocation to destLocation using bi-directional bfs
          
        """  
        if (origLocation == destLocation):#if no need to move, return true
            return True

        o_visited = []
        d_visited = []

        o_toVisit = []
        d_toVisit = []

        o_distance = 0
        d_distance = 0

        o_toVisit.append(origLocation)
        d_toVisit.append(destLocation)

        while (len(o_toVisit) > 0 or len(d_toVisit)> 0): # bi-directional bfs on path finding

            if d_distance < o_distance and len(d_toVisit) != 0:
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
        """ 
        let white piece move from origLocation to destLocation using dijkstra
          
        """  
        if origLocation == destLocation:
            return

        toVisit = [origLocation]
        shortestPath = {origLocation: [origLocation]}

        while destLocation not in shortestPath.keys():#dijkstra to find a path

            loc = toVisit.pop(0)

            for x in self.board.getValidMoveForPiece(loc):
                if x != destLocation and self.board.checkEaten(x):
                    continue

                if x in shortestPath.keys():
                    if len(shortestPath[loc])+1 < len(shortestPath[x]):
                        shortestPath[x] = shortestPath[loc]
                        shortestPath[x].append(x)
                else:
                    shortestPath[x] = copy.deepcopy(shortestPath[loc])
                    shortestPath[x].append(x)
                    toVisit.append(x)
        
        lastLoc = origLocation
        i = 0
    
        for path in shortestPath[destLocation]: #let piece move following the path

            if i == 0:
                i+=1
                continue

            self.board.executeMove(lastLoc,path)
            self.totalMove += 1
            lastx, lasty = lastLoc
            pathx, pathy = path
            print(str((lasty,lastx)) + " -> " + str((pathy,pathx))) #the output

            lastLoc = path


    def closestFriend(self, enemyLocation, friends):
        """ 
        return a list of friends location in the order of distance between them and enemyLocation
          
        """  
        distances = {}

        #compute all the distance
        for x in friends:
            distances[x] = self.distance(enemyLocation, x)

        #sort by the distance
        distances = sorted(distances, key = distances.get)

        return distances
        

    def distance(self, enenyLocation, myLocation):
        """ 
        compute the straight line distance between enemy and self
          
        """  
        x_enemy, y_enemy = enenyLocation
        x_me, y_me = myLocation

        return ((x_enemy-x_me)**2 + (y_enemy-y_me)**2)        
    
    def killPosition(self, enemyLocation):
        """ 
        return a list of positions needed to fill to kill eneny
          
        """  
        __killDirections = {
            "vertical": (1,0),
            "horizontal": (0,1),
        }

        result = []
        x_enemy,y_enemy = enemyLocation

        #loop through the __killDirections
        for x_dir,y_dir in __killDirections.values():

            #position 1
            x1 = x_enemy + x_dir
            y1 = y_enemy + y_dir

            #position 2
            x2 = x_enemy - x_dir
            y2 = y_enemy - y_dir

            positions = []

            #if one position is unable to reach, check next direction
            if x1 > 7 or y1 > 7 or self.board.pieces[x1][y1] == BLACK or self.board.pieces[x2][y2] == BLACK:
                continue

            #if reachable add to position
            if x1 < 8 and y1 < 8 and self.board.pieces[x1][y1] != BANNED:
                positions.append((x1, y1))
            if x1 < 8 and y1 < 8 and self.board.pieces[x2][y2] != BANNED:
                positions.append((x2, y2))

            #if first position is a trap, change the order
            if len(positions) == 2 and self.board.checkEaten(positions[0]):
                temp = positions[0]
                positions[0] = positions[1]
                positions[1] = temp

            #if both positions are traps, dont go
            if len(positions) == 2 and self.board.checkEaten(positions[0]) and self.board.checkEaten(positions[1]):
                continue

            result.append(positions)
        return result   
    
boardReader = BoardReader()
canoicalBoard, mode = boardReader.readInput()

board = Board(8, canoicalBoard)
if mode == "Moves":
    print(len(board.getAllLegalMoves(WHITE)))
    print(len(board.getAllLegalMoves(BLACK)))
elif mode == "Massacre":
    mass = Masscare(board)
    



