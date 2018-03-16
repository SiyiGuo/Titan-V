from partA import Board

EMPTY = "-"
BANNED = "X"
WHITE = "O"
BLACK = "@"

class Masscare(object):
    def __init__(self, board):
        self.board = Board(board)
        enemys = []
        friend = []
        for x in range(len(self.board.pieces)):
            for y in range(len(self.board.pieces[x])):
                if self.board.pieces[x][y] == BLACK:
                    self.enemys.append((x,y))
                elif self.board.pieces[x][y] == WHITE:
                    self.friend.append((x,y))
                
        self.killBlacks(enemys, fiends)
    
    def killBlacks(self, enemys, friends):
        while(len(enemys)>0):
            if self.kill(enemys[0]):
                enemys.remove(0)
    
    def kill(self, location, friends):
        #TODO: if killable, kill and return true
        #       else return false
    
    def move(self,origLocation, destLocation):
        #TODO: if white piece from orig can move to dest, move and return true ,else return fasle

    def closestFriend(self, enemyLocation, friends):
        for x,y in friends:

    def distance(self, enenyLocation, myLocation):
        x_enemy, y_enemy = enenyLocation
        x_me, y_me = myLocation
        return ((x_enemy-x_me)**2 + (y_enemy-y_me)**2)        
    
    def killPosition(self, enemyLocation):
        __killDirections = {
            "vertical": (1,0),
            "horizontal": (0,1),
        }

        blocks = [BLACK, EMPTY]
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
                position.append(x1, y1)
            if self.board.pieces[x2][y2] == EMPTY:
                position.append(x2, y2)
            result.append(positions)
        return result   