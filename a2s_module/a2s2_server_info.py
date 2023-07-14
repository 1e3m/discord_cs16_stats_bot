import a2s
import config
from texttable import Texttable
from datetime import datetime, time, timedelta

async def get_server_info():
    adr = (config.CS_SERVER_IP,config.CS_SERVER_PORT)
    info = a2s.info(adr)
    players = a2s.players(adr)
    return info, players

async def get_players_table(players):
    table = Texttable()
    table.set_cols_align(["l", "c", "r"])
    table.set_cols_valign(["t", "i", "a"])
    table.set_deco(Texttable.HEADER)
    pp = [['Ник','Фраги','Время в игре']]
    table.set_cols_width([25, 5, 15]) 
    for player in players:
        hour = int(player.duration / 3600)
        minutes = int((player.duration -hour*3600) / 60)
        seconds = int(player.duration - hour*3600 - minutes*60)
        player_time = time(hour,minutes,seconds)
        pp.append([player.name, player.score, player_time.strftime("%H:%M:%S")])
    table.add_rows(pp)        
    return table.draw()

async def get_current_map():
    adr = (config.CS_SERVER_IP,config.CS_SERVER_PORT)
    info = a2s.info(adr)
    return info.map_name