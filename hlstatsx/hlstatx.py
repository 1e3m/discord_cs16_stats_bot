from typing import List
from hlstatsx import hlstatsx_database
from hlstatsx.hlstatsx_hlx_player import HlxPlayer

ListHlxPLayers = List[HlxPlayer]

async def _get_hlxplayer_list(data) -> ListHlxPLayers:
    players = []
    if(data is not None):
        for p in data:
            players.append(HlxPlayer(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],p[13],p[14]))
    return players

async def get_player_id(steam_id: str, nick: str) -> int:
    if(steam_id is not None):
        steam_id = steam_id.split(':',1)[1]
    
    res = await hlstatsx_database.get_player_by_steam_id(steam_id)
    if(res is not None):
        return int(res[0])
    
    res = await hlstatsx_database.get_player_id_by_nick(nick)
    if(res is not None):
        return int(res[0])
    
    return None

async def get_pseudonym_player_stats(player_id: int) -> ListHlxPLayers:
    res = await hlstatsx_database.get_pseudonym_player_stats(player_id)
    players = await _get_hlxplayer_list(res)
    return players

async def get_top_players(players_count: int = 0) -> ListHlxPLayers:
    """get list range 10 HlxPlayers"""
    if(players_count < 10):
        players_count = 10
    start_number = players_count - 10
    res = await hlstatsx_database.get_top_players(start_number, players_count)
    return await _get_hlxplayer_list(res)

async def get_player_by_steam_id(steam_id) -> ListHlxPLayers:
    if(steam_id is None):
        return None
    steam_id = steam_id.split(':',1)[1]
    res = await hlstatsx_database.get_player_by_steam_id(steam_id)
    return await _get_hlxplayer_list(res)
        
async def get_player_by_nick(nick) -> HlxPlayer:
    """get HlxPLayer from nick"""
    res = await hlstatsx_database.get_player_by_nick(nick)
    if(res is not None):
        for p in res:
            return HlxPlayer(p[0],p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8],p[9],p[10],p[11],p[12],p[13],p[14])
    return None

async def get_all_players_nicks() -> ListHlxPLayers:
    """get list all nick players list(HlxPlayer) - only nicks fills"""
    players = []
    res = await hlstatsx_database.get_all_players_nicks()
    if(res is not None):
        for p in res:
            players.append(HlxPlayer.shortPlayer(p[0]))
    return players

#get_top_players(10)
