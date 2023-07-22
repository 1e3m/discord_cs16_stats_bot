import sqlite3
from sqlite3 import Error

import os
import sys

db_name = 'players_names.db'

tPlayers = 'players'

# determine if application is a script file or frozen exe
def _app_path():
    application_path = ""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path

def _create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = _dbOpen()
        return conn
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    _create_connection(f"{_app_path()}\\{db_name}")

def _dbOpen():
    conn = None
    try:
        conn = sqlite3.connect(f"{_app_path()}\\{db_name}")
        return conn
    except Error as e:
        print(e)

def _executeNonQuery(command, isPrint = True, *args):
    if isPrint:
        print(f'executeNonQuery: {command} {args}')
    conn = None
    try:
        conn = _dbOpen();
        cur = conn.cursor()
        if(args is not None):
            cur.execute(command, (args))
        else:
            cur.execute(command)
        return True
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.commit()
            conn.close()

def _execute(command, isPrint=True, *args):
    if isPrint:
        print(f'execute: {command} {args}')
    conn = None
    try:
        conn = _dbOpen();
        cur = conn.cursor()
        res = None
        if(args is not None):
            res = cur.execute(command, (args))
        else:
            res = cur.execute(command)
        r = res.fetchone()
        print(f'result: {r}')
        return r
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.commit()
            conn.close()

def _check_table(tableName):
    conn = _dbOpen();
    cur = conn.cursor()
    dbRes = cur.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tableName}' ''')
    r = dbRes.fetchone()
    result = False
    if r[0] != 0: 
        result = True
    else :
        result = False
    #commit the changes to db
    conn.commit()
    #close the connection
    conn.close()
    return result 

def _check_and_create_table(table):
    res = ''
    print(f'CHECK_TABLE {_check_table(table)}')
    if (_check_table(table) == False):
        res = _executeNonQuery(f''' CREATE TABLE {table}(player text NOT NULL pRIMARY KEY, nick text NULL, steam_id text NULL) ''', False)
    return res

def set_player(player_name, nick):
    """set player's nick to table 'players' (discord_user_id, nick)"""

    res = _check_and_create_table(tPlayers) #if table has not created -> create table

    if(_get_other_player_used_nick(nick, player_name) is not None): # if nick is used other user -> text error
        return "ОШИБКА! Введенный ник используется другим игроком!"

    if(_get_player(player_name) is not None): # if player already exist -> update, else -> insert
        if(_executeNonQuery(f''' UPDATE '{tPlayers}' set nick = ? where player = ?  ''', True, nick, player_name) == True):
            res = f'Ваш ник успешно обновлен на {nick}'       
    else:
        if(_executeNonQuery(f''' INSERT INTO {tPlayers}(player, nick) VALUES(?, ?) ''', True, player_name, nick) == True):
            res = f'Ваш ник успешно сохранен'
    return res

def set_steam_id(player_name, steam_id):
    """set steam id to table 'pLayers' (discord_user_id, steam_id)"""

    res = _check_and_create_table(tPlayers) #if table has not created -> create table
    if(_get_other_player_used_steam_id(steam_id, player_name) is not None): # if STEAM_ID is used other user -> text error
        return "ОШИБКА! Введенный STEAM_ID используется другим игроком!"

    if(_get_player(player_name) == True):  #if player already exist -> update, else -> insert
        if(_executeNonQuery(f''' UPDATE '{tPlayers}' set steam_id = ? where player = ?  ''', True, steam_id, player_name) == True):
           res = f'Ваш STEAM_ID успешно обновлен.'
    else:
        if(_executeNonQuery(f''' INSERT INTO {tPlayers}(player, steam_id) VALUES(?, ?) ''', True, player_name, steam_id) == True):
            res = f'Ваш STEAM_ID успешно сохранен'
    return res

def _get_player(player_name):
    """get player nick from db"""
    if(_check_table(tPlayers)):
        res = _execute(f''' SELECT nick FROM 'players' WHERE player = '{player_name}' ''')
        if res is None:
            return res
        return res[0]
    else:
        return None
    
def _get_other_player_used_nick(nick, player_name):
    """get other player user nick """
    if(_check_table(tPlayers)):
        res = _execute(f''' SELECT player FROM 'players' WHERE nick = ? and player <> ? ''', True, nick, player_name)
        if res is None:
            return res
        return res[0]
    else:
        return None
    
def _get_other_player_used_steam_id(steam_id, player_name):
    """get other player user steam_id """
    if(_check_table(tPlayers)):
        res = _execute(f''' SELECT player FROM 'players' WHERE steam_id = ? and player <> ? ''', True, steam_id, player_name)
        if res is None:
            return res
        return res[0]
    else:
        return None
    
def all_player():
    """all players"""
    if(_check_table(tPlayers)):
        res = _execute(f''' SELECT * FROM 'players' ''')
        print('ALL PLAYERS')
        print(res)
