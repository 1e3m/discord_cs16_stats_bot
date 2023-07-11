import discord
import config
import asyncio
import nest_asyncio
import token_cfg


from discord.ext import commands
from cogs.cs_bot import Cs_Cog


async def main():
    intents = discord.Intents.default()
    intents.message_content = True

    #bot.remove_command('help')   


    bot = commands.Bot(
        command_prefix='/',
        #command_prefix=commands.when_mentioned_or('/'),
        description='Статистика кс1.6 (help - /help_cs)',
        intents=intents
    )
    
    await bot.add_cog(Cs_Cog(bot))
    
    @bot.event
    async def on_ready():
        #await bot.load_extension("cogs.cs_bot")
        #await bot.load_extension(cogs.commands)        
        print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))



    bot.run(token_cfg.TOKEN)

nest_asyncio.apply()
asyncio.run(main())    

