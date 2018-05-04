import Arena
from Pubg.PubgGame import PubgGame, display
from Pubg.AlphaBetaPlayer import AbpPlayer


g = PubgGame(8)


abp4 = AbpPlayer(g, 1, abpDepth = 4).play
abp2 = AbpPlayer(g,1, abpDepth = 2).play

arena = Arena.Arena(abp2, abp2, g, display = display)
p1won, p2won, draws = arena.playGames(4, verbose = True)
print("p1Won:%s, p2Won:%s, draw:%s"%(p1won, p2won, draws))