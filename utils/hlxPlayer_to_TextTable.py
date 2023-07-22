from typing import List
from hlstatsx.hlstatsx_hlx_player import HlxPlayer
from texttable import Texttable

ListHlxPLayers = List[HlxPlayer]

async def __get_table() -> tuple:
    """return table columns annotation, and header row"""
    table = Texttable()
    table.set_cols_align(["l", "c", "r", "r", "r", "r", "r", "r"])
    table.set_cols_valign(["i", "t", "i", "i", "i", "i", "t", "t"])
    table.set_deco(Texttable.HEADER)
    pp = [['Место','Ник','Фраги','Смерти','В голову','k/d','Точность','Скилл']]
    return table , pp


async def get_text_table_from_list(players: ListHlxPLayers) -> str:
    """draw text tavle from list HlxPlayers"""
    table, rows = await __get_table()
    for p in players:        
        rows.append([p.player_rank, p.name, p.kills, p.deaths, p.headshots, p.kill_deaths, p.acuracy, p.skill ])
    table.add_rows(rows)        
    return table.draw()

async def get_text_table(player: HlxPlayer) -> str:
    """draw one row text table from HlxPLayer"""
    if(player is None):
        return None
    
    table, rows = await __get_table()        
    rows.append([player.player_rank, player.name, player.kills, player.deaths, player.headshots, player.kill_deaths, player.acuracy, player.skill ])
    table.add_rows(rows)        
    return table.draw()