import asyncio
from enum import Enum
import numpy as np

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
    X = '\U0000274C'  # :x:

    # FOR DEBUG
    # APPLE = 'A'  # :apple:
    # BLACK = 'B'  # :black_large_square:
    # DOWN = '\U00002B07'  # :arrow_down:
    # LEFT = '\U00002B05'  # :arrow_left:
    # RIGHT = '\U000027A1'  # :arrow_right:
    # SNAKE = 'S'  # :snake:
    # UP = '\U00002B06'  # :arrow_up:
    # X = '\U0000274C'  # :x:


class Game():
    """Inspired by https://github.com/jodylecompte/Anaconda for mechanics."""
    def __init__(self, size_x, size_y):
        self.size_x, self.size_y = size_x, size_y
        self.x, self.y = self.size_x//2, self.size_y//2  # starting position
        # a list of x-coords and y-coords
        self.body = [[self.x], [self.y]]
        self.score = 0
        self.is_over = False
        self.apple = ()

        self.screen = np.full((size_x, size_y), Emoji.BLACK.value)
        self.controls = (
            Emoji.LEFT.value,
            Emoji.UP.value,
            Emoji.DOWN.value,
            Emoji.RIGHT.value,
            Emoji.X.value,
        )

    async def play(self, ctx, bot):
        message = await ctx.send(self.display())  # starting screen
        for arrow in self.controls:
            await message.add_reaction(arrow)

        while not self.is_over:
            reaction, user = await bot.wait_for('reaction_add', timeout=None,
                check=lambda r, u: r.emoji in self.controls and u == ctx.author)
            await message.remove_reaction(reaction, user)

            if reaction.emoji == Emoji.UP.value:
                dx, dy = 0, -1
            elif reaction.emoji == Emoji.DOWN.value:
                dx, dy = 0, 1
            elif reaction.emoji == Emoji.RIGHT.value:
                dx, dy = 1, 0
            elif reaction.emoji == Emoji.LEFT.value:
                dx, dy = -1, 0
            elif reaction.emoji == Emoji.X.value:
                break

            self.move(dx, dy)

            await message.edit(content=self.display())

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.body[0].append(self.x)
        self.body[1].append(self.y)

        # move snake one block
        if len(self.body[0]) > self.score + 1:
            self.body[0] = self.body[0][1:]
            self.body[1] = self.body[1][1:]

    async def eat(self):
        self.score += 1

    async def game_over(self):
        self.is_over = True

    async def _spawn_apple(self):
        while True:
            apple = (
                np.random.randint(self.size_x),
                np.random.randint(self.size_y),
            )
            if apple not in np.asarray(self.body).T:
                self.apple = apple
                return

    def _reset_screen(self):
        self.screen = np.full((self.size_x, self.size_y), Emoji.BLACK.value)

    def display(self):
        self._reset_screen()
        print(self.body)
        self.screen[tuple(self.body)] = Emoji.SNAKE.value
        return '\n'.join(''.join(line) for line in self.screen.T)


class Snake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.dm_only()
    async def play(self, ctx, size_x=11, size_y=11):
        """Starts a game of Snake!"""
        # MAX SIZE IN NORMAL MESSAGE: 198 emojis (11 x 18)
        print('Starting Snake Game')

        game = Game(size_x, size_y)
        await game.play(ctx, self.bot)

        print('Snake Game Over')

    @commands.command()
    async def emoji(self, ctx):
        await ctx.send(' '.join(emoji.value for emoji in Emoji))


def setup(bot):
    bot.add_cog(Snake(bot))
