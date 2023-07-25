from hlstatsx import hlstatx_config 
from mysql.connector import connect, Error
from texttable import Texttable
        
async def _execute(sql_query):
	try:
		with connect(host=hlstatx_config.HOST, user=hlstatx_config.LOGIN, password=hlstatx_config.PASS, port=hlstatx_config.PORT, database=hlstatx_config.DATABASE) as connection:
			with connection.cursor() as cursor:
				cursor.execute(sql_query)
				result = cursor.fetchall()
				return result	
	except Error as e:
		print(e)
	finally:
		connection.close()

async def get_player_id_by_steam_id(steam_id: str):
	query = f"""
		SELECT * FROM u34670_hlstatsx.hlstats_playeruniqueids WHERE uniqueId = {steam_id}
	"""
	result = await _execute(query)
	return result

async def get_player_id_by_nick(nick: str):
	query = f"""
		SELECT playerId FROM hlstats_playernames WHERE name = {nick} 
	"""
	result = await _execute(query)
	return result

async def get_top_players(start_number, end_number):
	"""get range 10 players"""
	query = f'''
        SELECT
        	player_rank.player_rank,
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
		LEFT JOIN(
			SELECT 
				playerId rankPlayerId, 
				row_number() over (order by skill desc) player_rank 
			FROM u34670_hlstatsx.hlstats_players 
			order by skill desc
		) player_rank on hlstats_players.playerId = player_rank.rankPlayerId
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
	
	result = await _execute(query)
	return result

async def get_pseudonym_player_stats(player_id: int):
	query = f"""
	SELECT 
			ifnull(trank.player_rank,'') player_rank,
			pn.playerId,
			connection_time,
			name,
			null,
			null,
			null,
			kills,
			deaths,
			IFNULL(kills/deaths, '-') AS kpd,
			headshots,
			IFNULL(headshots/kills, '-') AS hpk,
			IFNULL(ROUND((hits / shots * 100), 1), 0.0) AS acc,
			null,
			null		
	FROM hlstats_playernames as pn
	left join (
		SELECT 
		playerId, 
		row_number() over (order by skill desc) player_rank, 
		lastName 
	FROM hlstats_players 
	order by skill desc
	) as Trank on Trank.playerId = pn.playerId and Trank.lastName = pn.name
	where pn.playerId = {player_id} 
	order by pn.lastuse desc;
	"""
	result = await _execute(query)
	return result

async def get_player_by_steam_id(steam_id: str):
	"""get statistic player from nick """	
	query = f'''
	SELECT
		player_rank.player_rank,
		hlstats_Players.playerId,
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
	INNER JOIN hlstats_playeruniqueids pUniq on pUniq.playerId = hlstats_Players.playerId
    LEFT JOIN(
		SELECT 
			playerId rankPlayerId, 
			row_number() over (order by skill desc) player_rank 
		FROM hlstats_players 
		order by skill desc
    ) player_rank on hlstats_players.playerId = player_rank.rankPlayerId
	WHERE
		hlstats_Players.game='cstrike'
		AND hideranking=0
		and pUniq.uniqueId = '{steam_id}'
	'''
	result = await _execute(query)
	return result

async def get_player_by_nick(nick: str):
	"""get statistic player from nick """
	query = f'''
	SELECT
		player_rank.player_rank,
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
    LEFT JOIN(
		SELECT 
			playerId rankPlayerId, 
			row_number() over (order by skill desc) player_rank 
		FROM hlstats_players 
		order by skill desc
    ) player_rank on hlstats_players.playerId = player_rank.rankPlayerId
	WHERE
		game='cstrike'
		AND hideranking=0
		and lastName = '{nick}'
	'''
	result = await _execute(query)
	return result

       
async def get_all_players_nicks():
	"""get list all players nicks""" 
	query = f'''
	SELECT DISTINCT
		lastName		
	FROM
		hlstats_Players
   	WHERE
		game='cstrike'
		AND hideranking=0
	'''
	result = await _execute(query)
	return result
