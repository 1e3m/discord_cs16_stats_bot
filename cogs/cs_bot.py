import discord
import urllib, json
import config
import csstats_mysql.table_stat as table_stat
import database
import aiohttp
import io
import traceback

from utils import hlxPlayer_to_TextTable
from a2s_module import a2s2_server_info
from hlstatsx import hlstatx

import asyncio
import datetime
import asyncpg

from discord.ext import tasks, commands
from discord import app_commands
from requests_html import AsyncHTMLSession

async def setup(client):
   	await client.add_cog(commands(client))

class Cs_Cog(commands.Cog):

	cs_channel = ""
	#tree = ""

	def __init__(self, bot):
		self.bot = bot
		self.index = 0		
		self.cs16_map = ''
		self.bot_version = '0.02_pikaby'
		#Cs_Cog.tree = app_commands.CommandTree(client)
		#self.batch_update.add_exception_type(asyncpg.PostgresConnectionError)
		

	def cog_unload(self):
		self.status_timer.cancel()
		self.top_timer.cancel()

	def check_channel(interaction: discord.Interaction) -> bool:
		return interaction.channel.id == Cs_Cog.cs_channel

	@commands.Cog.listener()
	async def on_ready(self):
		print('ready')
		channels = self.bot.get_all_channels();
		for ch in channels:
			if(ch.name == config.CS_CHANNEL):
				Cs_Cog.cs_channel = ch.id
				database.create_connection()
				break
		self.status_timer.start()
		self.top_timer.start()
		return

	@commands.command()
	async def sync(self, ctx) -> None:
		fmt = await ctx.bot.tree.sync()
		await ctx.send(f"Synced {len(fmt)} commands.")

	#@app_commands.command(name="ping", description="тестовая команда пинга")
	#async def ping(self, interaction: discord.Interaction):
	#	bot_latency = round(self.bot.latency * 1000)
	#	await interaction.response.send_message(f"Pong! {bot_latency} ms.")

	#@bot.tree.command(name='sync', description='Owner only')
	#async def sync(interaction: discord.Interaction):
	#	if interaction.user.id == '389436856435212290' or interaction.user.id == '606849840843849738':
	#		await Cs_Cog.tree.sync()
	#		print('Command tree synced.')
	#	else:
	#		await interaction.response.send_message('You must be the owner to use this command!')	

	#def test(self):
	#	asyncio.run(self.top_timer_tick_async())
	utc = datetime.timezone.utc
	time_top = datetime.time(hour=22, minute=15, tzinfo=utc)

	@tasks.loop(time = time_top, reconnect = True)			
	async def top_timer(self):
		print("top_timer")
		now = datetime.datetime.now()
		#if(now.hour == 0):
		ch = self.bot.get_channel(Cs_Cog.cs_channel)
		msg = await table_stat.get_table_stats(10)
	    #print(msg)
		await ch.send('```' + msg + f'```\n from:  {config.HLX_STATS_URL}' )



	@tasks.loop(seconds=1800, reconnect = True)
	async def status_timer(self):
		print("status_timer")
		await self.get_server_status_for_loop()

	async def get_server_status_for_loop(self):
		startCmdTime = datetime.datetime.now()

		map = a2s2_server_info.get_current_map();
		if(self.cs16_map == map):
			return
		self.cs16_map = map
		
		ch = self.bot.get_channel(Cs_Cog.cs_channel)
		try:
			msg = await self.get_server_status()
			file = await self.get_banner()			
			await ch.send(msg, file=discord.File(file, "server_status.png"))
			c_time = await self.command_time(startCmdTime)
			await self.lem_log(startCmdTime, self.bot.user ,'/server status cycle', c_time, ch.guild.name)			
		except Exception as e:
			await ch.send(f'\n```Сервер недоступен```')
			await self.lem_log_stack_trace(startCmdTime, self.bot.user ,'status cycle', 0, ch.guild.name, traceback.format_exc()) 

	
	async def command_time(self, date):
		return (datetime.datetime.now() - date).total_seconds()

	async def lem_log(self, startTime, user, command, timeCommand, guild):
		lem = await self.bot.fetch_user(389436856435212290)
		await lem.send(f'```time: {startTime}, user: {user}, command: {command}, command_time: {timeCommand} sec. server: {guild}``` bot_ver:{self.bot_version}')

	async def lem_log_stack_trace(self, startTime, user, command, timeCommand, guild, stack):
		lem = await self.bot.fetch_user(389436856435212290)
		await lem.send(f'```time: {startTime}, user: {user}, command: {command}, command_time(method): {timeCommand} sec. server: {guild}```\nstack trace: ```{stack}``` bot_ver: {self.bot_version}')

	async def get_banner(self):
		result = None
		async with aiohttp.ClientSession() as session: # creates session
			async with session.get(config.SERVER_STATUS_URL) as resp: # gets image from url
				img = await resp.read() # reads image from response
				#with io.BytesIO(img) as file: # converts to file-like object
				result = io.BytesIO(img)
		return result
	

	async def get_server_status(self):
		info, players = await a2s2_server_info.get_server_info()
		msg = ""
		if(info is not None and players is not None):
			msg += f'---\nСервер: ```{info.server_name}```\nТекущая карта:```{info.map_name}```\nИгроки на сервере: {len(players)}/32'
			players_msg = ""
			if(len(players) > 0):
				tbl_players = await a2s2_server_info.get_players_table(players)
		msg = f'{msg}``` {tbl_players}```'		
		return f'\n{msg}\n Подключиться: ```connect {config.CS_SERVER_IP}:{config.CS_SERVER_PORT}```'		

	@app_commands.command(name="status", description="Строка подключения к серверу, картинка со статусом сервера")
	@app_commands.check(check_channel)
	async def status(self, interaction: discord.Interaction):
		startCmdTime = datetime.datetime.now()
		await interaction.response.defer()
		try:
			msg =  await self.get_server_status()
			file = await self.get_banner()
			await interaction.followup.send(msg, file=discord.File(file, "server_status.png"))			
		except Exception as e:
			await interaction.followup.send(f'\n```Сервер недоступен```')
			await self.lem_log_stack_trace(startCmdTime, interaction.user.name ,'/status', 0, interaction.guild.name, traceback.format_exc())

	# @app_commands.command(name="players_online", description="Текущая карта, список игроков онлайн")
	# @app_commands.check(check_channel)
	# async def players_online(self, interaction: discord.Interaction):
	# 	expire = f'{interaction.expires_at}'
	# 	try:
	# 		await interaction.response.defer(ephemeral=True)
	# 	except Exception as e:
	# 		print('expiring:')
	# 		print(expire)
	# 		print(f'now: {datetime.datetime.now()}')
	# 		await self.lem_log_stack_trace(datetime.datetime.now(), interaction.user.name ,'/players_online', 0, interaction.guild.name, traceback.format_exc())

	# 	print("players_online")
	# 	if(interaction.is_expired() == True):
	# 		print("timeout")
	# 		return

	# 	#await asyncio.sleep(5)
	# 	startCmdTime = datetime.datetime.now()
	# 	try:
	# 		server_info = await self.online_status()
	# 		print('server_info')
	# 		print(server_info)
	# 		self.cs16_map = server_info.current_map
	# 		PlayersOnlineStr = '\n'.join(server_info.players) 
	# 		msg = f'Текущая карта: ```{server_info.current_map}```\n Игроки на сервере({len(server_info.players)}/30):\n```\n\n{PlayersOnlineStr}```'; 


	# 		async with aiohttp.ClientSession() as session: # creates session
	# 			async with session.get(config.SERVER_STATUS_URL) as resp: # gets image from url
	# 				img = await resp.read() # reads image from response
	# 				with io.BytesIO(img) as file: # converts to file-like object
	# 					c_time = await self.command_time(startCmdTime);
	# 					#emb = discord.Embed()
	# 					#emb.description = "Подключиться к серверу через Стим [Ссылка](steam://connect/46.174.52.22:27212)"
	# 					await interaction.followup.send(f'\n{msg}\n Подключиться: ```connect {config.CS_SERVER_IP}:{config.CS_SERVER_PORT}```', file=discord.File(file, "server_status.png"))#, embed = emb)
	# 					await self.lem_log(startCmdTime, interaction.user.name ,'/players_online', c_time, interaction.guild.name)
	# 					#await interaction.response.send_message()
	# 	except Exception as e:
	# 		await interaction.followup.send(f'\n```Сервер недоступен```')
	# 		#await interaction.response.send_message()
	# 		await self.lem_log_stack_trace(startCmdTime, interaction.user.name ,'/players_online', 0, interaction.guild.name, traceback.format_exc())
	# 		print(e)

	@app_commands.command(name="top", description="Список игроков, от текущего значения 10 игроков вверх")
	@app_commands.check(check_channel)
	async def top(self, interaction: discord.Interaction, players_count: int = 10):
		if players_count < 10:
			players_count = 10
		players = await hlstatx.get_top_players(players_count)
		msg = await hlxPlayer_to_TextTable.get_text_table_from_list(players)
		#msg = await table_stat.get_table_stats(players_count)
		await interaction.response.send_message('```' + msg + f'```\n from:  {config.HLX_STATS_URL}' )

	#@commands.command(name='player_cs')
	#async def player_cs(self,ctx,*args):

	@app_commands.command(name="player_cs", description="Статистика игрока")
	@app_commands.check(check_channel)
	async def player_cs(self, interaction: discord.Interaction, nick: str):		
		await interaction.response.defer()
		startCmdTime = datetime.datetime.now()
		try:
			#await asyncio.sleep(5)
			#arg = ' '.join(args)
			nick = nick.strip()
			#print(nick)
			player = await table_stat.get_table_player(nick);
			c_time = await self.command_time(startCmdTime);
			if(player == 0):
				await interaction.followup.send(f'```Игрок с ником {nick} не найден, проверьте правильность написания ника.```' )
				await self.lem_log(startCmdTime, interaction.user.name ,'/player_cs', c_time, interaction.guild.name)
			else:
				await interaction.followup.send(f'```{player}```\n from:  {config.HLX_STATS_URL}' )
				await self.lem_log(startCmdTime, interaction.user.name ,'/player_cs', c_time, interaction.guild.name)
		except Exception as e:
			await self.lem_log_stack_trace(startCmdTime, interaction.user.name ,'/player_cs', 0, interaction.guild.name, traceback.format_exc())

	@app_commands.command(name="help_cs", description="Справка")
	@app_commands.check(check_channel)
	async def help_cs(self, interaction: discord.Interaction):	        
		await interaction.response.send_message('```' + config.MSG_HELP + '```' )

	@app_commands.command(name="info_cs", description="Инфо")
	@app_commands.check(check_channel)
	async def info_cs(self, interaction: discord.Interaction): 
		await interaction.response.send_message('```' + config.MSG_INFO + '```' )

	@app_commands.command(name="nick_cs", description="Сохранить свой ник, для вызова команды /rank_cs")
	@app_commands.check(check_channel)
	async def nick_cs(self, interaction: discord.Interaction, nick: str):
		id = interaction.user.id
		await interaction.response.send_message(f'``` '+ database.setPlayer(id ,nick) + '```')

	# @app_commands.command(name="rank", description="Ваша статистика по сохраненному нику командой /nick_cs")
	# @app_commands.check(check_channel)
	# async def rank(self, interaction: discord.Interaction): 
	# 	await interaction.response.defer()
	# 	startCmdTime = datetime.datetime.now()
	# 	try:
	# 		#await asyncio.sleep(5)	
	# 		nick = interaction.user.name + '#' + interaction.user.discriminator
	# 		cs_nick = database.getPlayer(nick)
	# 		player = await table_stat.get_table_player(cs_nick, True);
	# 		c_time = await self.command_time(startCmdTime);
	# 		if(player == 0):
	# 			await interaction.followup.send(f'```Ваша статистика не найдена.\nПроверьте, правильно ли вы указали боту свой ник командой nick_cs\nИли, возможно, вы еще не играли.```' )
	# 			await self.lem_log(startCmdTime, interaction.user.name ,'/rank', c_time, interaction.guild.name)
	# 		else:
	# 			await interaction.followup.send(f'```{player}```\n from:  {config.HLX_STATS_URL}' )
	# 			await self.lem_log(startCmdTime, interaction.user.name ,'/rank', c_time, interaction.guild.name)
	# 	except Exception as e:
	# 		await self.lem_log_stack_trace(startCmdTime, interaction.user.name ,'/rank', 0, interaction.guild.name, traceback.format_exc())

	@app_commands.command(name="rank", description="Ваша статистика по сохраненному нику командой /nick_cs")
	@app_commands.check(check_channel)
	async def rank(self, interaction: discord.Interaction): 
		await interaction.response.defer()
		startCmdTime = datetime.datetime.now()
		try:
			#await asyncio.sleep(5)	
			#nick = interaction.user.name + '#' + interaction.user.discriminator
			id = interaction.user.id
			cs_nick = database.getPlayer(id)
			player = await hlstatx.get_player(cs_nick);
			c_time = await self.command_time(startCmdTime);
			if(player is None):
				await interaction.followup.send(f'```Ваша статистика не найдена.\nПроверьте, правильно ли вы указали боту свой ник командой nick_cs\nИли, возможно, вы еще не играли.```' )
				await self.lem_log(startCmdTime, interaction.user.name ,'/rank', c_time, interaction.guild.name)
			else:
				text_table = await hlxPlayer_to_TextTable.get_text_table(player)
				await interaction.followup.send(f'```{text_table}```\n from:  {config.HLX_STATS_URL}' )
				await self.lem_log(startCmdTime, interaction.user.name ,'/rank', c_time, interaction.guild.name)
		except Exception as e:
			await self.lem_log_stack_trace(startCmdTime, interaction.user.name ,'/rank', 0, interaction.guild.name, traceback.format_exc())


	async def online_status(self):
		#print(config.MONITORING_SERVER_URL)
		responce = ''
		try:
			asession = AsyncHTMLSession()		
			asession.encoding = 'utf-8'
			responce = await asession.get(config.MONITORING_SERVER_URL)
			responce.html.encoding = 'utf-8'
			responce.encoding = 'utf-8'
			await responce.html.arender(sleep=1,keep_page=True)

			responce.html.encoding = 'utf-8'
			responce.encoding = 'utf-8'
			
			if responce is None:
				return None
			#print('p1')
			content = responce.html.find('#content',first=True);
			#print('p2')
			players_info = responce.html.find('.playersserver',first=True)
			#print('p3')
			server_info = responce.html.find('.gameserver',first=True)
			#print('p4')
			if(server_info is not None):
				current_map = str(bytes(server_info.find('#mapname',first=True).text,'utf-8'),'utf-8', errors='replace')

			#players_info.encoding = 'utf-8'
			playersOnline = []
			if(players_info is not None):
				#print('p5')
				players = players_info.find('.name-list')
		
				for p in players:
					#print('player:' + p.text)
					#print(str(bytes(p.text,'utf-8'),'utf-8', errors='replace'))
					pl = str(bytes(p.text,'utf-8'),'utf-8', errors='replace')
					#print(pl)
					playersOnline.append(pl)

			info = ServerInfo(current_map, playersOnline)
			return info
		except Exception as e:
			print(e)
			raise e
		finally:
			await responce.session.close()

class ServerInfo():
	def __init__(self,current_map, players):
		self.current_map = current_map
		self.players = players