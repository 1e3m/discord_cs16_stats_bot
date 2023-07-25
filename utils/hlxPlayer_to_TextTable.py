from typing import List
from hlstatsx.hlstatsx_hlx_player import HlxPlayer
from texttable import Texttable

ListHlxPLayers = List[HlxPlayer]
Column_aling = List[str]
Column_header = List[List[str]]

_default_cols_align = ["l", "c", "r", "r", "r", "r", "r", "r"]
_default_cols_valign = ["i", "t", "i", "i", "i", "i", "t", "t"]
_default_header = [['Место','Ник','Фраги','Смерти','В голову','k/d','Точность','Скилл']]

async def __get_table(cols_align: Column_aling, cols_valign: Column_aling, header = Column_header) -> tuple:
    """return table columns annotation, and header row"""
    table = Texttable()
    table.set_cols_align(cols_align)   #(["l", "c", "r", "r", "r", "r", "r", "r"])
    table.set_cols_valign(cols_valign)  #(["i", "t", "i", "i", "i", "i", "t", "t"])
    table.set_deco(Texttable.HEADER)
    pp =  header.copy()  #[['Место','Ник','Фраги','Смерти','В голову','k/d','Точность','Скилл']]
    return table , pp

async def get_text_players_from_list(players: ListHlxPLayers, cols_align: Column_aling = _default_cols_align, cols_valign: Column_aling = _default_cols_valign, header: Column_header = _default_header) -> str:
    """draw text tavle from list HlxPlayers"""
    table, rows = await __get_table(cols_align,cols_valign, header)
    for p in players:        
        rows.append([p.player_rank, p.name, p.kills, p.deaths, p.headshots, p.kill_deaths, p.acuracy, p.skill ])
    table.add_rows(rows)        
    return table.draw()

async def get_text_pseudonyms_players_from_list(players: ListHlxPLayers, cols_align: Column_aling = _default_cols_align, cols_valign: Column_aling = _default_cols_valign, header: Column_header = _default_header) -> str:
    """draw text tavle from list HlxPlayers"""
    table, rows = await __get_table(cols_align,cols_valign, header)
    for p in players:        
        rows.append([p.player_rank, p.name, p.kills, p.deaths, p.headshots, p.kill_deaths, p.acuracy])
    table.add_rows(rows)        
    return table.draw()

async def get_text_player_table(player: HlxPlayer, cols_align: Column_aling = _default_cols_align, cols_valign: Column_aling = _default_cols_valign, header: Column_header = _default_header) -> str:
    """draw one row text table from HlxPLayer"""
    if(player is None):
        return None
    
    table, rows = await __get_table(cols_align,cols_valign, header)        
    rows.append([player.player_rank, player.name, player.kills, player.deaths, player.headshots, player.kill_deaths, player.acuracy, player.skill ])
    table.add_rows(rows)        
    return table.draw()