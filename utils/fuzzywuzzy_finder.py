from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from typing import List
from hlstatsx.hlstatsx_hlx_player import HlxPlayer

ListHlxPLayers = List[HlxPlayer]
ListStr = List[str]

async def get_players_collection_for_find(players: ListHlxPLayers) -> ListStr:
    """get list of string names of players for fuzzywuzzy source collection for find"""
    players_collection_for_find = []
    for p in players:
        players_collection_for_find.append(p.name)
    return players_collection_for_find

async def find_player(nick: str, players: ListHlxPLayers) -> str:   
    """find player from list for nick,
    \nfuzzywuzzy ration > 91
    """    
    search_player = process.extractOne(nick, await get_players_collection_for_find(players))

    if search_player[1] < 91:
        return 0
    
    search_player = search_player[0]
    return search_player

async def find_five_alternative_players(nick: str, players: ListHlxPLayers) -> str:
    """find 5 alternative players from nick"""  
    collection_for_search = await get_players_collection_for_find(players)
    search_players = process.extract(nick,collection_for_search , limit = 5)
    player_names = []

    for p in search_players:
        player_names.append(p[0])
    return ' , '.join(player_names)