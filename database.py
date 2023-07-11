import sqlite3
from sqlite3 import Error

import os
import sys

db_name = 'players_names.db'

tPlayers = 'players'

# determine if application is a script file or frozen exe
def app_path():
    application_path = ""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path



def create_connection():
    """ create a database connection to a SQLite database """
    conn = None
    try:
        #print("db_path:")
        #print(f"{app_path()}\\{db_name}")
        conn = sqlite3.connect(f"{app_path()}\\{db_name}")
        return conn
        #print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    create_connection(f"{app_path()}\\{db_name}")

def dbOpen():
    conn = None
    try:
        #print("db_path:")
        #print(f"{app_path()}\\{db_name}")
        conn = sqlite3.connect(f"{app_path()}\\{db_name}")
        return conn
        #print(sqlite3.version)
    except Error as e:
        print(e)

def executeNonQuery(command, isPrint = True, *args):
    if isPrint:
        print(f'executeNonQuery: {command} {args}')
    c = None
    try:
        c = dbOpen();
        cur = c.cursor()
        if(args is not None):
            cur.execute(command, (args))
        else:
            cur.execute(command)
        return True
    except Error as e:
        print(e)
    finally:
        if c:
            c.commit()
            c.close()

def execute(command, isPrint=True):
    if isPrint:
        print(f'execute: {command}')
    c = None
    try:
        c = dbOpen();
        cur = c.cursor()
        res = cur.execute(command)
        r = res.fetchone()
        print(f'result: {r}')
        return r
    except Error as e:
        print(e)
    finally:
        if c:
            c.commit()
            c.close()

def check_table(tableName):
    c = dbOpen();
    cur = c.cursor()
    #print(f'check_table: SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{tableName}"')
    dbRes = cur.execute(f''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tableName}' ''')
    r = dbRes.fetchone()
    #print(f'qRes: {r}')
    result = False
    #print('fetchAll: ' + str(r[0]))
    if r[0] != 0: 
        result = True
    else :
        result = False
    #commit the changes to db
    c.commit()
    #close the connection
    c.close()
    return result 

def setPlayer(player_name, nick):
    res = ''
    print(f'CHECK_TABLE {check_table(tPlayers)}')
    if (check_table(tPlayers) == False):
        res = executeNonQuery(f''' CREATE TABLE {tPlayers}(player text NOT NULL pRIMARY KEY, nick text NULL) ''', False)

    if(getPlayer(player_name) is not None):
        if(executeNonQuery(f''' UPDATE '{tPlayers}' set nick = ? where player = ?  ''', True, nick, player_name) == True):
            res = f'Ваш ник успешно обновлена на {nick}'       
    else:
        if(executeNonQuery(f''' INSERT INTO {tPlayers}(player, nick) VALUES(?, ?) ''', True, player_name, nick) == True):
            res = f'Ваш ник успешно сохранен'
    return res


def getPlayer(player_name):

    if(check_table(tPlayers)):
        res = execute(f''' SELECT nick FROM 'players' WHERE player = '{player_name}' ''')
        if res is None:
            return res
        return res[0]
    else:
        return None

def all_player():
    if(check_table(tPlayers)):
        res = execute(f''' SELECT * FROM 'players' ''')
        print('ALL PLAYERS')
        print(res)
