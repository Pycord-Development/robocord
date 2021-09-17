"""
The MIT License (MIT)

Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import discord
import os
import sys
import asyncio
import psutil
import logging
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='eval')
    async def _eval(self, ctx, *, code: codeblock_converter):
        """Eval some code"""
        cog = self.bot.get_cog("Jishaku")
        await cog.jsk_python(ctx, argument=code)

    @commands.command(name='refresh')
    async def _refresh(self, ctx):
        """Refresh the bot by invoking `jsk git pull` and `restart`"""
        cog = self.bot.get_cog("Jishaku")
        await cog.jsk_git(ctx, argument=codeblock_converter('pull'))
        await asyncio.sleep(2)  # allow jsk git pull to finish
        restart = self.bot.get_command('restart')
        await ctx.invoke(restart)

    @commands.command(name='restart')
    async def _restart(self, ctx):
        """
        Restart the bot.
        """
        embed = discord.Embed(title="Be right back!")
        await ctx.send(embed=embed)
        self.bot.cache['restart_channel'] = ctx.channel.id
        if sys.stdin.isatty():
            try:
                p = psutil.Process(os.getpid())
                for handler in p.open_files() + p.connections():
                    os.close(handler.fd)
            except Exception as e:
                logging.error(e)
            python = sys.executable
            os.execl(python, python, *sys.argv)
        await self.bot.logout()
        embed = ctx.error('Failed to restart')
        await ctx.send(embed=embed)

    @commands.command(name='shutdown', aliases=['off', 'die', 'shut', 'kill'])
    async def _shutdown(self, ctx):
        await ctx.send(embed=ctx.embed(title='Shutting Down'))
        if sys.stdin.isatty():
            await self.bot.logout()
        else:
            self.bot.hang = True
            await self.bot.logout()

    @commands.command(name='sudo', aliases=['su'])
    async def _sudo(self, ctx):
        """
        Reinvoke someone's command, running with all checks overridden
        """
        try:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except discord.errors.NotFound:
            return await ctx.send(embed=ctx.error('I couldn\'t find that message'))
        await ctx.message.add_reaction('\U00002705')
        context = await ctx.bot.get_context(message)
        await context.reinvoke()

    async def cog_check(self, ctx):
        return ctx.author.id in self.bot.owner_ids


def setup(bot):
    bot.add_cog(Owner(bot))
