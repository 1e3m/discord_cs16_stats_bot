import hlstatx_config 
from mysql.connector import connect, Error
from texttable import Texttable


#import mariadb

# connection parameters
# conn_params= {
#     "user" : hlstatx_config.LOGIN,
#     "password" : hlstatx_config.PASS,
#     "host" : hlstatx_config.HOST,
#     "database" : hlstatx_config.DATABASE
# }




def mySql_connect():
    print("connecting to MySQL")
    try:
        with connect(
            host=hlstatx_config.HOST,
            user=hlstatx_config.LOGIN,
            password=hlstatx_config.PASS,
            port=3306,
            database=hlstatx_config.DATABASE
        ) as connection:
            print(connection)
            return connection
    except Error as e:
        print(e)

def get_top_players(start_number, end_number):
    select_top = f'''
        SELECT
			playerId,
			connection_time,
			lastName,
			flag,
			country,
			skill,
			kills,
			deaths,
			IFNULL(kills/deaths, '-') AS kpd,
			headshots,
			IFNULL(headshots/kills, '-') AS hpk,
			IFNULL(ROUND((hits / shots * 100), 1), 0.0) AS acc,
			activity,
			last_skill_change
		FROM
			hlstats_Players
		WHERE
			game='cstrike'
			AND hideranking=0
		ORDER BY
			skill desc,
			lastName ASC
		LIMIT
			{start_number},
			{end_number}
    '''

    #conn= mariadb.connect(**conn_params)
    conn =  mySql_connect()
    conn.reconnect()
    with conn.cursor() as cursor:
        cursor.execute(select_top)
        result = cursor.fetchall()
        return result
