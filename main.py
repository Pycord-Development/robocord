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
import inspect
import os
import time

import discord
from discord import SlashCommand, Option, SlashCommandGroup, option, OptionChoice, AllowedMentions
from discord.ext import commands

from tools import Bot, send_code, get_prefix

bot = Bot(command_prefix=get_prefix,
          case_insensitive=True,
          strip_after_prefix=True,
          intents=discord.Intents.all(),
          activity=discord.Activity(type=discord.ActivityType.watching, name="Pycord"),
          description="The official pycord bot")

brainfuck = bot.create_group("bf", "Commands related to brainfuck.")
github = bot.create_group("github", "Commands related to github.")

repo = 'https://github.com/Pycord-Development/pycord'

for cog in bot.config.get('cogs', []):
    try:
        bot.load_extension(cog)
        print(cog)
    except discord.DiscordException:
        if __name__ == "__main__":
            print(f'!!! {cog} !!!')
        else:
            raise


@brainfuck.command()
async def encode(ctx, text: Option(str, "Text to encode in brainfuck")):
    """Encode text into brainfuck."""
    encoded = bot.brainfuck.encode(text)
    await send_code(ctx, encoded.code, lang="bf")


@brainfuck.command(name="compile")
async def _compile(ctx, code: Option(str, "Brainfuck code to compile into python")):
    """Compile brainfuck into python."""
    compiled = bot.brainfuck.compile(code)
    await send_code(ctx, compiled.code, lang="py")


@brainfuck.command()
async def decode(ctx, code: Option(str, "Brainfuck code to decode into text")):
    """Decode brainfuck into text."""
    decoded = bot.brainfuck.decode(code)
    await send_code(ctx, decoded.text, lang="txt", filename="text.txt")


@bot.slash_command()
async def invite(ctx):
    """Invite me to your server."""
    permissions = 2134207679
    url = discord.utils.oauth_url(client_id=bot.user.id, permissions=discord.Permissions(permissions=permissions),
                                  scopes=("bot", "applications.commands"))
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Invite", url=url))
    await ctx.respond("I'm glad you want to add me to your server, here's a link!", view=view)


@bot.slash_command()
async def ping(ctx):
    """Get the latency of the bot."""
    latencies = {
        "websocket": bot.latency,
    }

    def comp_message():
        msgs = []
        for title in latencies:
            msgs.append(f"{title.title()}: {(latencies[title] * 1000):.0f}ms")
        return '\n'.join(msgs)

    start = time.perf_counter()
    await ctx.respond(comp_message())
    end = time.perf_counter()

    latencies["round trip"] = end - start

    await ctx.edit(content=comp_message())


@github.command()
async def issue(ctx, number: Option(int, "Issue number")):
    """View an issue from the pycord github repo."""
    url = f"{repo}/issues/{number}"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="View Issue", url=url))
    await ctx.respond(f"Here's a link", view=view)


@github.command()
async def pr(ctx, number: Option(int, "Pull request number")):
    """View a pull request from the pycord github repo."""
    url = f"{repo}/issues/{number}"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="View Pull Request", url=url))
    await ctx.respond(f"Here's a link", view=view)



@bot.slash_command()
async def source(ctx, command: Option(str, "The command to view the source code for", required=False)):
    """View the source for a particular command or the whole bot."""
    source_url = 'https://github.com/Pycord-Development/robocord'
    branch = 'main'
    view = discord.ui.View()
    if command is None:
        url = source_url
        label = "Source code for entire bot"
    else:
        command_split = command.split()
        index = 0
        obj = discord.utils.get(bot.application_commands.values(), name=command_split[index])
        while isinstance(obj, SlashCommandGroup):
            if index + 1 > len(command_split):
                return await ctx.respond("Error: Command is a group. You must choose a subcommand from it.")
            obj = discord.utils.get(obj.subcommands, name=command_split[index])
        if not isinstance(obj, SlashCommand):
            return await ctx.respond("Error: Command could not be found")
        # noinspection PyUnresolvedReferences
        src = obj.callback.__code__
        filename = src.co_filename
        lines, firstlineno = inspect.getsourcelines(src)
        location = os.path.relpath(filename).replace('\\', '/')

        url = f'{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}'
        content = await discord.ext.commands.clean_content(escape_markdown=True).convert(ctx, command)
        label = f'Source code for command "{content}"'
    view.add_item(discord.ui.Button(label="View Code", url=url))
    await ctx.respond(label, view=view)


@bot.user_command(name="Join Position")
async def _joinpos(ctx, member):
    all_members = list(ctx.guild.members)
    all_members.sort(key=lambda m: m.joined_at)

    def _ord(n):
        return str(n) + (
            "th"
            if 4 <= n % 100 <= 20
            else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        )
    await ctx.respond(f"{member.mention} was the {_ord(all_members.index(member) + 1)} person to join {ctx.guild.name}", allowed_mentions=AllowedMentions(users=False))

role_option = Option(
    int,
    description="The role you want added",
    choices = [
        OptionChoice("Events", 915701572003049482),
        OptionChoice("Tester", 881968560635805706),
    ])
@bot.slash_command(name="role", guild_ids=[881207955029110855])
async def _role(ctx, name: role_option):
    """Claim roles in the server"""
    role_id = name
    assert role_id in (915701572003049482, 881968560635805706)
    role = guild.get_role(role_id)
    if not role:
        await ctx.respond("Error: Couldn't find that role")
    elif not role in ctx.author.roles:
        await ctx.author.add_roles(role)
        await ctx.respond(f"Added {role.mention} role")
    else:
        await ctx.author.remove_roles(role)
        await ctx.respond(f"Removed {role.mention} role")


class Developer(commands.Cog):

    def __init__(self, bot_):
        self.bot = bot_

    @commands.command(name='load', aliases=['l'])
    @commands.is_owner()
    async def _load(self, ctx, cog_, save: bool = False):
        if save:
            val = self.bot.config.get('cogs', [])
            val.append(cog_)
            self.bot.config['cogs'] = val
        self.bot.load_extension(cog_)
        await ctx.send(f'Loaded cog "{cog_}"{" (saved)" if save else ""}')

    @commands.command(name='unload', aliases=['u'])
    @commands.is_owner()
    async def _unload(self, ctx, cog_, save: bool = False):
        if save:
            val = self.bot.config.get('cogs', [])
            val.remove(cog_)
            self.bot.config['cogs'] = val
        self.bot.unload_extension(cog_)
        await ctx.send(f'Unloaded cog "{cog_}"{" (saved)" if save else ""}')

    @commands.command(name='reload', aliases=['r'])
    @commands.is_owner()
    async def _reload(self, ctx, cog_):
        self.bot.reload_extension(cog_)
        await ctx.send(f'Reloaded cog "{cog_}"')

    @commands.command(name='loadall', aliases=['la'])
    @commands.is_owner()
    async def _loadall(self, ctx):
        data = self.bot.config.setdefault('cogs', [])
        cogs = {
            'loaded': [],
            'not': []
        }
        for cog_ in data:
            if cog_ in bot.extensions:
                continue
            try:
                self.bot.load_extension(cog_)
                cogs['loaded'].append(cog_)
            except discord.DiscordException:
                cogs['not'].append(cog_)

        await ctx.send('\n'.join([
            ('\U00002705' if cog_ in cogs['loaded'] else '\U0000274c')
            + cog_ for cog_ in data]) or "No cogs to load")

    @commands.command(name='unloadall', aliases=['ua'])
    @commands.is_owner()
    async def _unloadall(self, ctx):
        cogs = {
            'unloaded': [],
            'not': []
        }
        processing = bot.extensions.copy()
        for cog_ in processing:
            try:
                self.bot.unload_extension(cog_)
                cogs['unloaded'].append(cog_)
            except discord.DiscordException:
                cogs['not'].append(cog_)
        await ctx.send('\n'.join([
            ('\U00002705' if cog_ in cogs['unloaded'] else '\U0000274c')
            + cog_ for cog_ in processing]) or "No cogs to unload")

    @commands.command(name='reloadall', aliases=['ra'])
    @commands.is_owner()
    async def _reloadall(self, ctx):
        cogs = {
            'reloaded': [],
            'not': []
        }
        processing = bot.extensions.copy()
        for cog_ in processing:
            try:
                self.bot.reload_extension(cog_)
                cogs['reloaded'].append(cog_)
            except discord.DiscordException:
                cogs['not'].append(cog_)
        await ctx.send('\n'.join([
            ('\U00002705' if cog_ in cogs['reloaded'] else '\U0000274c')
            + cog_ for cog_ in processing]) or "No cogs to reload")


bot.add_cog(Developer(bot))


@bot.event
async def on_ready():
    print("ready")
    restart_channel = bot.cache.get("restart_channel")
    if restart_channel:
        print("Restarted")
        del bot.cache["restart_channel"]
        channel = bot.get_channel(restart_channel)
        await channel.send("I'm back online")
    else:
        print(f"Logged in as {bot.user}")
    await bot.storage.setup_db()


@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:  # invoke the command again on edit
        if not after.author.bot:
            ctx = await bot.get_context(after)
            await bot.invoke(ctx)

@bot.event
async def on_message(message):
	if bot.afk_users.get(message.author.id):
			del bot.afk_users[message.author.id]
			return await message.channel.send(f'Welcome back {message.author.name}, you are no longer AFK')

	for mention in message.mentions:
		if bot.afk_users.get(mention.id):
				return await message.channel.send(f'{mention.name} is AFK: {bot.afk_users[mention.id]}', allowed_mentions = discord.AllowedMentions.none())

	await bot.process_commands(message)
          
bot.afk_users = {}
          
          
slowmode = bot.command_group(name='slowmode', description="Slowmode related commands for moderators", guild_ids=guild_ids)

@slowmode.command(name='set', description='Set the slowmode of the current channel')
@commands.has_role(881407111211384902)
async def set(ctx, time:Option(int, 'Enter the time in seconds')):
	if ctx.author.guild_permissions.manage_messages:
	
		if time > 21600:
			await ctx.respond(content=f"Slowmode of a channel must be {humanize.precisedelta(21600)} (21600 seconds) or less.", ephemeral=True)
		else:
			await ctx.channel.edit(slowmode_delay=time)
			await ctx.respond(f"The slowmode of this channel has been changed to {humanize.precisedelta(time)} ({time}s)")
	else:
		await ctx.respond("You do not have the `Manage Message` permission which is required to run this command.", ephemeral=True)

@slowmode.command(name='off', description='Remove the slowmode from the current channel')
@commands.has_role(881407111211384902)
async def off(ctx):
	if ctx.author.guild_permissions.manage_messages:
		if ctx.channel.slowmode_delay == 0:
			await ctx.respond(content="This channel doesn't have a slowmode. Use `/slowmode set` to set a slowmode.", ephemeral=True)
		await ctx.channel.edit(slowmode_delay=0)
		await ctx.respond("Removed the slowmode from this channel!")
	else:
		await ctx.respond("You do not have the `Manage Message` permission which is required to run this command.", ephemeral=True)

for i in ["jishaku", "cogs.rtfm", "cogs.modmail", "cogs.tags"]:
    bot.load_extension(i)

afk = bot.command_group(name='afk', description='AFK Commands', guild_ids=guild_ids)

@afk.command(name='set')
async def afk_set(ctx, *, reason = 'No reason provided'):
	if bot.afk_users.get(ctx.author.id):
		return await ctx.send(f'{ctx.author.name}, you\'re already AFK')
	if len(reason) > 100: # so that chat doesn't flood when the reason has to be shown 
		return await ctx.send(f'{ctx.author.name}, keep your AFK reason under 100 characters') 
	bot.afk_users[ctx.author.id] = reason
	await ctx.send(f'{ctx.author.name}, I set your AFK with the reason: {reason}', allowed_mentions=discord.AllowedMentions.none(), ephemeral=True) 

@afk.command(name='remove')
async def afk_remove(ctx):
	if bot.afk_users.get(ctx.author.id):
			del bot.afk_users[ctx.author.id]
			return await ctx.send(f'Welcome back {ctx.author.name}, you are no longer AFK')
          

if __name__ == "__main__":
    bot.run()
    if bot.hang:
        # We want to prevent this from finishing, but the bot is logged out
        while True:
            time.sleep(60)
