import asyncio
from enum import Enum
import numpy as np
import pickle

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


class Score():
    try:
        with open('high_scores.pkl', 'rb') as f:
            high_scores = pickle.load(f)

    except FileNotFoundError as e:
        high_scores = {}

    @classmethod
    def save(cls, size, user_id, score):
        """Saves the score, if it is higher than the previous one.
        size: tuple (size_x, size_y) of the game played.
        user_id: int of the Discord user ID.
        score: int of the user's score.
        """
        try:
            size_scores = cls.high_scores[size]
        except KeyError:
            # user has no data yet, we create one for the given size and score
            cls.high_scores[size] = {user_id: score}
        else:
            # user has data, we check if it has one of given size
            try:
                size_scores[user_id] = max(size_scores[user_id], score)
            except KeyError:
                # user has no data for the given size, we create it
                size_scores[user_id] = score

        # save the scores on file.
        with open('high_scores.pkl', 'wb') as f:
            pickle.dump(cls.high_scores, f)

    @classmethod
    def get(cls, size, user_id):
        """Returns a user's high score in a given size. If user has no score,
        return None."""
        try:
            return cls.high_scores[size][user_id]
        except KeyError:
            return None

    @classmethod
    def get_top(cls, size):
        """Returns only the highest score of a given size. Returns None if it
        does not exist yet."""
        try:
            return max(cls.high_scores[size].values())
        except KeyError:
            return None

    @classmethod
    def get_top_users(cls, size):
        """Returns a list of users ID with the highest score in a given size.
        Returns an empty list if no scores are available at this size."""
        try:
            size_scores = cls.high_scores[size]
        except KeyError:
            return []
        else:
            top_score = max(size_scores.values())

            # assume more than one user can have top score
            top_users = []
            for k in size_scores.keys():
                if size_scores[k] == top_score:
                    top_users.append(k)

            return top_users

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

        self.embed = discord.Embed(
            title='A Game of Snake',
            type='rich',
            url='https://github.com/Snaptraks/SnakeBot',
            color=0x77B255,
        ).set_footer(
            text='Coded for Discord Hack Week by Snaptraks#2606',
        # ).set_author(
        #     name='Snaptraks#2606',
        #     url='https://github.com/Snaptraks',
        ).add_field(
            name='Personnal Best',
            value=Score.get((self.size_x, self.size_y), self.ctx.author.id),
        ).add_field(
            name='High Score',
            value=Score.get_top((self.size_x, self.size_y)),
        ).add_field(
            # name=(
            #     ':regional_indicator_s: '
            #     ':regional_indicator_n: '
            #     ':regional_indicator_a: '
            #     ':regional_indicator_k: '
            #     ':regional_indicator_e: '
            # ),
            name=f'Score: {self.score}',
            value=self.display(),
            inline=False,
        )

        self.controls = (
            Emoji.LEFT.value,
            Emoji.UP.value,
            Emoji.DOWN.value,
            Emoji.RIGHT.value,
            Emoji.X.value,
        )

    async def play(self):
        # message_game = await self.ctx.send(self.display())  # starting screen
        # message_game = await self.ctx.send(embed=self.display())  # starting screen
        message_game = await self.ctx.send(embed=self.embed)  # starting screen
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

            # Detect collision with apple
            if (self.x, self.y) == self.apple:
                # print('moved over apple')
                self.eat()
            if self._apple_eaten:
                self._spawn_apple()

            # Detect collision with itself
            body = np.asarray(self.body).T
            body = body[:-1].tolist()
            head_in_body = [part == [self.x, self.y] for part in body]
            if any(head_in_body):
                await self.game_over('hit itself')
                continue

            # Detect collision with border
            if (self.x < 0 or
                self.x >= self.size_x or
                self.y < 0 or
                self.y >= self.size_y):
                # game over
                await self.game_over('hit a wall')
                continue

            # Update message with new game layout
            # await message_game.edit(content=self.display())
            # await message_game.edit(embed=self.display())
            await self.update_display()

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
        Score.save((self.size_x, self.size_y), self.ctx.author.id, self.score)


    def _spawn_apple(self):
        body = np.asarray(self.body).T
        while True:
            apple = (
                np.random.randint(self.size_x),
                np.random.randint(self.size_y),
            )
            apple_in_body = [part == list(apple) for part in body.tolist()]
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
        str_screen = '\n'.join(''.join(line) for line in self.screen.T)
        return str_screen

    async def update_display(self):
        self.embed.set_field_at(
            index=2,
            name=f'Score: {self.score}',
            value=self.display(),
            inline=False,
        )
        await self.message_game.edit(embed=self.embed)


class Snake(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, size_x=5, size_y=5):
        """Starts a game of Snake!"""
        # MAX SIZE IN NORMAL MESSAGE: 198 emojis (18 x 11)
        if size_x > 18:
            size_x = 18
        elif size_x < 5:
            size_x = 5
        if size_y > 11:
            size_y = 11
        elif size_y < 5:
            size_y = 5
        print('Starting Snake Game')

        game = Game(size_x, size_y, ctx, self.bot)
        await game.play()

        print('Snake Game Over')

    @commands.command()
    async def emoji(self, ctx):
        """Prints all the emojis (for debugging)."""
        await ctx.send(' '.join(emoji.value for emoji in Emoji))


def setup(bot):
    bot.add_cog(Snake(bot))
