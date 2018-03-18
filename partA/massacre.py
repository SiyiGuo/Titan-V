from partA import Board

EMPTY = "-"
BANNED = "X"
WHITE = "O"
BLACK = "@"

class Masscare(object):
    def __init__(self, board):
        self.board = Board(board)
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
        while(len(enemys)>0):
            if self.kill(enemys[0], friends):
                enemys.remove(0)
    
    def kill(self, location, friends):
        x_enemy, y_enemy = location
        closeFriends = self.closestFriend(location,friends)
        killPos = self.killPosition(location)
        for pos in killPos:
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
                loc = d_toVisit.remove(0)
                d_visited.append(loc)
                toVisit = self.board.getValidMoveForPiece(loc)
                for x in toVisit:
                    if x not in d_visited:
                        d_toVisit.append(x)
                d_distance += 1

            else:
                loc = o_toVisit.remove(0)
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
            loc = toVisit.remove(0)
            for x in self.board.getValidMoveForPiece(loc):
                if x in shortestPath.keys():
                    if len(shortestPath[loc])+1 < len(shortestPath[x]):
                        shortestPath[x] = shortestPath[loc]
                        shortestPath[x].append(x)
                else:
                    shortestPath[x] = shortestPath[loc]
                    shortestPath[x].append(x)
        lastLoc = origLocation
        for path in shortestPath[destLocation]: 
            self.board.executeMove(lastLoc,path)
            lastLoc = path         


    def closestFriend(self, enemyLocation, friends):
        distances = {}
        for x in friends:
            distances[x] = self.distance(enemyLocation, x)
        distances = sorted(distances)
        return distances.keys()
        

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
            if self.board.pieces[x1][y1] == BLACK or self.board.pieces[x2][y2] == BLACK:
                continue
            if self.board.pieces[x1][y1] == EMPTY:
                positions.append(x1, y1)
            if self.board.pieces[x2][y2] == EMPTY:
                positions.append(x2, y2)
            result.append(positions)
        return result   