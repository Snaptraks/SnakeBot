import asyncio
import discord
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def stop(self, ctx):
        """Stops the bot quickly."""
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, module):
        """Loads a cog/module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.message.add_reaction('\N{CROSS MARK}')
            raise
        else:
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, module):
        """Reloads a cog/module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.message.add_reaction('\N{CROSS MARK}')
            raise
        else:
            await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')


def setup(bot):
    bot.add_cog(Admin(bot))
