import asyncio
import discord
from discord.ext.commands import Bot
from discord.ext import commands

import config

class MyBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        invitation_link = (f'https://discordapp.com/oauth2/authorize?'
            f'client_id={self.user.id}&scope=bot&permissions=68672')
        print(invitation_link)

if __name__ == '__main__':
    bot = MyBot(description='SnakeBot by Snaptraks#2606',
        command_prefix='!',
        help_command=commands.DefaultHelpCommand(dm_help=False)
    )

    start_cogs = [
        'cogs.Admin',
        'cogs.Snake',
    ]

    for cog in start_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            # Do something clever here
            raise e

    asyncio.get_event_loop().run_until_complete(bot.start(config.bot_token))
