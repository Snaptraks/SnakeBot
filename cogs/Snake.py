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
    def __init__(self, size_x, size_y, ctx, bot):
        self.size_x, self.size_y = size_x, size_y
        self.ctx, self.bot = ctx, bot

        self.x, self.y = self.size_x//2, self.size_y//2  # starting position
        # a list of x-coords and y-coords
        self.body = [[self.x], [self.y]]
        self.score = 0
        self.is_over = False
        self.apple = ()
        self._apple_eaten = True

        self.screen = np.full((size_x, size_y), Emoji.BLACK.value)
        self.controls = (
            Emoji.LEFT.value,
            Emoji.UP.value,
            Emoji.DOWN.value,
            Emoji.RIGHT.value,
            Emoji.X.value,
        )

    async def play(self):
        message_game = await self.ctx.send(self.display())  # starting screen
        self.message_game = message_game
        for arrow in self.controls:
            await message_game.add_reaction(arrow)

        def check(reaction, user):
            return reaction.emoji in self.controls and\
                user == self.ctx.author

        # initial speed
        dx, dy = 0, -1

        while not self.is_over:
            try:
                reaction, user = await self.bot.wait_for('reaction_add',
                    timeout=1.5,
                    check=check)
            except asyncio.TimeoutError as e:
                pass
            else:
                await message_game.remove_reaction(reaction, user)

                if reaction.emoji == Emoji.UP.value:
                    dx, dy = 0, -1
                elif reaction.emoji == Emoji.DOWN.value:
                    dx, dy = 0, 1
                elif reaction.emoji == Emoji.RIGHT.value:
                    dx, dy = 1, 0
                elif reaction.emoji == Emoji.LEFT.value:
                    dx, dy = -1, 0
                elif reaction.emoji == Emoji.X.value:
                    await self.game_over('cancelled')
                    continue

            self.move(dx, dy)

            if (self.x, self.y) == self.apple:
                print('moved over apple')
                self.eat()
            if self._apple_eaten:
                self._spawn_apple()

            # Detect collision with itself
            if len(self.body[0]) > 1:
                for bx, by in zip(*self.body):
                    pass

            # Detect collision with border
            if (self.x < 0 or
                self.x >= self.size_x or
                self.y < 0 or
                self.y >= self.size_y):
                # game over
                await self.game_over('hit a wall')
                continue

            # Update message with new game layout
            await message_game.edit(content=self.display())

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.body[0].append(self.x)
        self.body[1].append(self.y)

        # move snake one block
        if len(self.body[0]) > self.score + 1:
            self.body[0] = self.body[0][1:]
            self.body[1] = self.body[1][1:]

    def eat(self):
        self.score += 1
        self._apple_eaten = True

    async def game_over(self, reason):
        self.is_over = True
        # await self.message_game.delete()
        await self.message_game.clear_reactions()
        print(reason)

    def _spawn_apple(self):
        body = np.asarray(self.body).T
        while True:
            apple = (
                np.random.randint(self.size_x),
                np.random.randint(self.size_y),
            )
            apple_in_body = [row == list(apple) for row in body.tolist()]
            if not any(apple_in_body):
                self.apple = apple
                self._apple_eaten = False
                return

    def _reset_screen(self):
        self.screen = np.full((self.size_x, self.size_y), Emoji.BLACK.value)

    def display(self):
        self._reset_screen()
        # set Apple location
        if self.apple:
            self.screen[self.apple] = Emoji.APPLE.value
        # set Snake body
        self.screen[tuple(self.body)] = Emoji.SNAKE.value
        # Transpose (.T) the screen array to match horizontal-x vertical-y in
        # (x, y) order, unlike (i, j) for matrices
        return '\n'.join(''.join(line) for line in self.screen.T)


class Snake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    # @commands.dm_only()
    async def play(self, ctx, size_x=5, size_y=5):
        """Starts a game of Snake!"""
        # MAX SIZE IN NORMAL MESSAGE: 198 emojis (18 x 11)
        if size_x > 18:
            size_x = 18
        if size_y > 11:
            size_y = 11
        print('Starting Snake Game')

        game = Game(size_x, size_y, ctx, self.bot)
        await game.play()

        print('Snake Game Over')

    @commands.command()
    async def emoji(self, ctx):
        await ctx.send(' '.join(emoji.value for emoji in Emoji))


def setup(bot):
    bot.add_cog(Snake(bot))
