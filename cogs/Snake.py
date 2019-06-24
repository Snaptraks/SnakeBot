import asyncio
from enum import Enum

import discord
from discord.ext import commands


class Emoji(Enum):
    APPLE = '\U0001F34E'  # :apple:
    BLACK = '\U00002B1B'  # :black_large_square:
    DOWN = '\U00002B07'  # :arrow_down:
    LEFT = '\U00002B05'  # :arrow_left:
    RIGHT = '\U000027A1'  # :arrow_right:
    SNAKE = '\U0001F40D'  # :snake:
    UP = '\U00002B06'  # :arrow_up:
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
