from hlstatsx import hlstatsx_database
from hlstatsx.hlstatsx_hlx_player import HlxPlayer
from texttable import Texttable



async def get_top_players(players_count: int = 0):
    if(players_count < 10):
        players_count = 10
    start_number = players_count - 10;
    res = await hlstatsx_database.get_top_players(start_number, players_count)
    players = []
    if(res is not None):
        for p in res:
            players.append(HlxPlayer(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],p[13],p[14]))

    return players
        
async def get_player(nick):
    res = await hlstatsx_database.get_player(nick)
    if(res is not None):
        for p in res:
            return HlxPlayer(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],p[13],p[14])

#get_top_players(10)
