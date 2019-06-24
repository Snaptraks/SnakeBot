import asyncio
from enum import Enum

import discord
from discord.ext import commands


class Emoji():
    APPLE = '🍎'
    BLACK = '⬛'
    DOWN = '⬇️'
    LEFT = '⬅️'
    RIGHT = '➡️'
    SNAKE = '🐍'
    UP = '⬆️'
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
