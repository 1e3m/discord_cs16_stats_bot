import discord
import urllib, json
import config
import csstats_mysql.table_stat as table_stat
import database
import aiohttp
import io
import traceback
import re

from cogs import server_commands
from utils import fuzzywuzzy_finder, hlxPlayer_to_TextTable
from utils import discord_color_textblock as textblock
from utils import discord_text_colors as textcolor
from steam_communication import a2s2_server_info, steam_id_finder
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
	utc = datetime.timezone.utc

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
		channels = self.bot.get_all_channels()
		for ch in channels:
			if(ch.name == config.CS_CHANNEL):
				Cs_Cog.cs_channel = ch.id
				database._create_connection()
				break
		self.status_timer.start()
		self.top_timer.start()
		return

	@commands.command()
	async def sync(self, ctx) -> None:
		fmt = await ctx.bot.tree.sync()
		await ctx.send(f"Synced {len(fmt)} commands.")

	time_top = datetime.time(hour=22, minute=15, tzinfo=utc)
	@tasks.loop(time = time_top, reconnect = True)			
	async def top_timer(self):
		print("top_timer")
		now = datetime.datetime.now()
		ch = self.bot.get_channel(Cs_Cog.cs_channel)
		msg = await table_stat.get_table_stats(10)
		await ch.send('```' + msg + f'```\n from: {config.HLX_STATS_URL}' )

	@tasks.loop(seconds=1800, reconnect = True)
	async def status_timer(self):
		print("status_timer")
		await self.get_server_status_for_loop()

	time_server_commands = datetime.time(hour=9, minute=0, tzinfo=utc)
	@tasks.loop(time = time_server_commands, reconnect = True)
	async def server_commands_loop(self):
		ch = self.bot.get_channel(Cs_Cog.cs_channel)
		commands = await self.get_server_commands_info()
		ch.send(commands)

	async def get_server_commands_info(self):
		info = ''
		for key, value in server_commands.COMMANDS.items():
			info += f'```{key} - {value}```'
		return f'.\n\nСписок доступных команд на сервере во время игры:\n{info}'
	
	@app_commands.command(name="game_commands", description="Список доступных команд на сервере во время игры")
	@app_commands.check(check_channel)
	async def game_commands(self, interaction: discord.Interaction):
		startCmdTime = datetime.datetime.now()
		await interaction.response.defer()
		try:			
			c_time = await self.command_time(startCmdTime)
			commands = await self.get_server_commands_info()
			await interaction.followup.send(commands)
			await self.lem_log(startCmdTime, self.bot.user ,'/commands', c_time, interaction.guild.name)			
		except Exception as e:
			await self.lem_log_stack_trace(startCmdTime, self.bot.user ,'commands', 0, interaction.guild.name, traceback.format_exc()) 

	async def get_server_status_for_loop(self):
		startCmdTime = datetime.datetime.now()
		map = a2s2_server_info.get_current_map()

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
			await ch.send(f'\n{await self.get_server_timeout_message()}')
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

	async def get_server_timeout_message(self) -> str:
		return await textblock.get_ansi_block(await textblock.colorize(textcolor.Red,"Сервер недоступен"))

	async def get_server_status(self):
		info, players = await a2s2_server_info.get_server_info()
		msg = ""
		if(info is not None and players is not None):
			server_name = await textblock.get_ansi_block(await textblock.colorize(textcolor.Red,f'{info.server_name}'))
			map_name = await textblock.get_ansi_block(await textblock.colorize(textcolor.Cyan,info.map_name))
			msg += f'---\nСервер: {server_name}\nТекущая карта:{map_name}'
			players_msg = ""
		players_count = 0
		player_table = ""
		if(players is not None):
			if(len(players) > 0):
				players_count = len(players)
				player_table = await a2s2_server_info.get_players_table(players)
		player_table = await textblock.get_ansi_block(await textblock.colorize(textcolor.Blue,player_table))
		msg = f'{msg}\nИгроки на сервере: {players_count}/32  {player_table}'	
		connect_ip = await textblock.get_ansi_block(await textblock.colorize(textcolor.Orange_background,f'connect {config.CS_SERVER_IP}:{config.CS_SERVER_PORT}'))
		return f'\n{msg}\n Подключиться: {connect_ip}'		

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
			await interaction.followup.send(f'\n{await self.get_server_timeout_message()}')
			await self.lem_log_stack_trace(startCmdTime, interaction.user.name ,'/status', 0, interaction.guild.name, traceback.format_exc())
	
	@app_commands.command(name="top", description="Список игроков, от текущего значения 10 игроков вверх")
	@app_commands.check(check_channel)
	async def top(self, interaction: discord.Interaction, players_count: int = 10):
		if players_count < 10:
			players_count = 10
		players = await hlstatx.get_top_players(players_count)
		msg = await hlxPlayer_to_TextTable.get_text_players_from_list(players)
		msg = await textblock.get_ansi_block(await textblock.colorize(textcolor.Cyan,msg))
		await interaction.response.send_message(f'{msg}\n from:  {config.HLX_STATS_URL}' )

	@app_commands.command(name="player_cs", description="Статистика игрока")
	@app_commands.check(check_channel)
	async def player_cs(self, interaction: discord.Interaction, nick: str):		
		await interaction.response.defer()
		startCmdTime = datetime.datetime.now()
		try:
			nick = nick.strip()
			all_players = await hlstatx.get_all_players_nicks()
			search_nick = await fuzzywuzzy_finder.find_player(nick, all_players)
			player = await hlstatx.get_player_by_nick(search_nick)
			tbl_player = await hlxPlayer_to_TextTable.get_text_player_table(player)
			c_time = await self.command_time(startCmdTime)
			if(player is None):
				alternative_players = await fuzzywuzzy_finder.find_five_alternative_players(nick,all_players)
				msg = await textblock.get_ansi_block(await textblock.colorize(textcolor.Red,f"Игрок с ником {nick} не найден, проверьте правильность написания ника."))
				msg_alternative_players = await textblock.get_ansi_block("Возможно вы искали одного из этих игроков: " + await textblock.colorize(textcolor.Cyan,alternative_players))
				await interaction.followup.send(f'{msg}\n{msg_alternative_players}' )
				await self.lem_log(startCmdTime, interaction.user.name ,'/player_cs', c_time, interaction.guild.name)
			else:
				await interaction.followup.send(f'```{tbl_player}```\n from:  {config.HLX_STATS_URL}' )
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
		error, res = database.set_player(id ,nick)
		color = textcolor.Red if error else textcolor.Cyan
		msg = await textblock.get_ansi_block(await textblock.colorize(color,res))
		await interaction.followup.send(f'{res}')

	@app_commands.command(name="steam_id", description="Сохранить STEAM_ID в базу для mix сервера")
	@app_commands.check(check_channel)
	async def steam_id(self, interaction: discord.Interaction, steam_id: str): 
		await interaction.response.defer()
		expression = r"/(?P<CUSTOMPROFILE>https?\:\/\/steamcommunity.com\/id\/[A-Za-z_0-9]+)|(?P<CUSTOMURL>\/id\/[A-Za-z_0-9]+)|(?P<PROFILE>https?\:\/\/steamcommunity.com\/profiles\/[0-9]+)|(?P<STEAMID2>STEAM_[10]:[10]:[0-9]+)|(?P<STEAMID3>\[U:[10]:[0-9]+\])|(?P<STEAMID64>[^\/][0-9]{8,})/g"
		search = re.search(expression,steam_id.strip())

		if(search is None):
			err_msg = await textblock.get_ansi_block(await textblock.colorize(textcolor.Red,"Ошибка! Введен некорректный STEAM_ID. Необходимо ввести STEAM_ID в формате STEAM_X:X:X...X"))
			await interaction.followup.send(err_msg)

		if(steam_id_finder.chek_steam_id(steam_id)):
			msg = await textblock.get_ansi_block(await textblock.colorize(textcolor.Cyan,f"STEAM_ID: {steam_id}\nкоманда работает в тестовом режиме, и ничего не делает"))
			await interaction.followup.send(msg)		
		error, res = database.set_steam_id(interaction.user.id,f'{steam_id}')
		color = textcolor.Red if error else textcolor.Cyan
		msg = await textblock.get_ansi_block(await textblock.colorize(color,res))
		await interaction.followup.send(f'{res}')

	@app_commands.command(name="steam_id_from_comunity_url", description="Сохранить STEAM_ID в базу для mix сервера по ссылку на профиль STEAM")
	@app_commands.check(check_channel)
	async def steam_id_from_comunity_url(self, interaction: discord.Interaction, url: str): 
		await interaction.response.defer()
		steam_id = await steam_id_finder.get_steam_id_from_url(url)
		error, res = database.set_steam_id(interaction.user.id,f'{steam_id}')
		color = textcolor.Red if error else textcolor.Cyan
		msg = await textblock.get_ansi_block(await textblock.colorize(color,res))
		await interaction.followup.send(f'{res}')

	@app_commands.command(name="rank", description="Ваша статистика по сохраненному нику командой /nick_cs")
	@app_commands.check(check_channel)
	async def rank(self, interaction: discord.Interaction): 
		await interaction.response.defer()
		startCmdTime = datetime.datetime.now()
		try:
			id = interaction.user.id
			cs_nick, steam_id = database._get_player(id)
			player = await hlstatx.get_player_by_steam_id(steam_id)
			player_finded_by_steam_id = True
			if(player is None):			
				player = await hlstatx.get_player_by_nick(cs_nick)
				player_finded_by_steam_id = False
			c_time = await self.command_time(startCmdTime)
			if(player is None):
				err_msg = await textblock.get_ansi_block(await textblock.colorize(textcolor.Red,"Ваша статистика не найдена.\nПроверьте, правильно ли вы указали боту свой ник командой nick_cs\nИли, возможно, вы еще не играли."))
				await interaction.followup.send(err_msg )
				await self.lem_log(startCmdTime, interaction.user.name ,'/rank', c_time, interaction.guild.name)
			else:
				if player_finded_by_steam_id:
					text_table = await hlxPlayer_to_TextTable.get_text_players_from_list(player)
					player_id = player[0].player_id
				else:
					text_table = await hlxPlayer_to_TextTable.get_text_player_table(player)
					player_id = player.player_id
				pseudonims = await hlstatx.get_pseudonym_player_stats(player_id)
				pseudonims_texttable = await hlxPlayer_to_TextTable.get_text_pseudonyms_players_from_list(pseudonims,["l", "c", "r", "r", "r", "r", "r"],["i", "t", "i", "i", "i", "i", "t"],[['Место','Ник','Фраги','Смерти','В голову','k/d','Точность']])
				main_stat = await textblock.get_ansi_block(await textblock.colorize(textcolor.Blue,text_table))
				pseudonym_block = await textblock.get_ansi_block(await textblock.colorize(textcolor.Green,pseudonims_texttable))
				await interaction.followup.send(f'{main_stat}\nПсевдонимы на сервере: {pseudonym_block}\n from:  {config.HLX_STATS_BASE_URL}?mode=playerinfo&player={player_id}' )
				await self.lem_log(startCmdTime, interaction.user.name ,'/rank', c_time, interaction.guild.name)
		except Exception as e:
			await self.lem_log_stack_trace(startCmdTime, interaction.user.name ,'/rank', 0, interaction.guild.name, traceback.format_exc())