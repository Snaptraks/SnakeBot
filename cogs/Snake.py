import asyncio

import discord
from discord.ext import commands


class Snake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def play(self, ctx, size=10):
        """Starts a game of Snake!"""
        pass



def setup(bot):
    bot.add_cog(Snake(bot))
