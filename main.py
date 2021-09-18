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
from discord import SlashCommand
from discord.app import Option, SlashCommandGroup
from discord.ext import commands

from tools import Bot, send_code, get_prefix


class HelpCommand(commands.HelpCommand):
    def get_ending_note(self):
        return "Use p!{0} [command] for more info on a command.".format(
            self.invoked_with
        )

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = "|".join(command.aliases)
            fmt = f"[{command.name}|{aliases}]"
            if parent:
                fmt = f"{parent}, {fmt}"
            alias = fmt
        else:
            alias = command.name if not parent else f"{parent} {command.name}"
        return f"{alias} {command.signature}"

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Robocord", color=discord.Color.blurple())
        description = self.context.bot.description
        if description:
            embed.description = description

        for cog_, cmds in mapping.items():
            name = "Other Commands" if cog_ is None else cog_.qualified_name
            filtered = await self.filter_commands(cmds, sort=True)
            if filtered:
                value = "\u002C ".join(f"`{c.name}`" for c in cmds)
                if cog_ and cog_.description:
                    value = "{0}\n{1}".format(cog_.description, value)

                embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog_):
        embed = discord.Embed(title="{0.qualified_name} Commands".format(cog_))
        if cog_.description:
            embed.description = cog_.description

        filtered = await self.filter_commands(cog_.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(
                name=self.get_command_signature(command),
                value=command.short_doc or "...",
                inline=False,
            )

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=group.qualified_name)
        if group.help:
            embed.description = group.help

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(
                    name=self.get_command_signature(command),
                    value=command.short_doc or "...",
                    inline=False,
                )

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    # This makes it so it uses the function above
    # Less work for us to do since they're both similar.
    # If you want to make regular command help look different then override it
    send_command_help = send_group_help


bot = commands.Bot(
    command_prefix=get_prefix,
    description="The Official Pycord Bot",
    case_insensitive=True,
    help_command=HelpCommand(),
    activity=discord.Activity(
        type=discord.ActivityType.competing, name="the fork race"
    ),
    intents=discord.Intents.all()
)

bot.owner_ids = [
    690420846774321221, #bobdotcom
    571638000661037056,  # BruceDev (pleeeeease)
]

brainfuck = bot.command_group("bf", "Commands related to brainfuck.")
github = bot.command_group("github", "Commands related to github.")

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
    url = f"{repo}/pulls/{number}"
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
        src = obj.callback.__code__
        filename = src.co_filename
        lines, firstlineno = inspect.getsourcelines(src)
        location = os.path.relpath(filename).replace('\\', '/')

        url = f'{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}'
        content = await discord.ext.commands.clean_content(escape_markdown=True).convert(ctx, command)
        label = f'Source code for command "{content}"'
    view.add_item(discord.ui.Button(label="View Code", url=url))
    await ctx.respond(label, view=view)


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


@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:  # invoke the command again on edit
        if not after.author.bot:
            ctx = await bot.get_context(after)
            await bot.invoke(ctx)
          
          
#### ERROR HANDLER

@bot.event
async def on_command_error(ctx, error):
    exception = error
    if hasattr(ctx.command, "on_error"):
        pass
    error = getattr(error, "original", error)

    if ctx.author.id in ctx.bot.owner_ids:
        if isinstance(
                error,
            (
                commands.MissingAnyRole,
                commands.CheckFailure,
                commands.DisabledCommand,
                commands.CommandOnCooldown,
                commands.MissingPermissions,
                commands.MaxConcurrencyReached,
            ),
        ):
            try:
                await ctx.reinvoke()
            except discord.ext.commands.CommandError:
                pass
            else:
                return

    if isinstance(
            error,
        (
            commands.BadArgument,
            commands.MissingRequiredArgument,
            commands.NoPrivateMessage,
            commands.CheckFailure,
            commands.DisabledCommand,
            commands.CommandInvokeError,
            commands.TooManyArguments,
            commands.UserInputError,
            commands.NotOwner,
            commands.MissingPermissions,
            commands.BotMissingPermissions,
            commands.MaxConcurrencyReached,
            commands.CommandNotFound,
        ),
    ):
        if not isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="Oops! Something went wrong...",
                description=f"Reason: {str(error)}",
                color=discord.Color.red(),
            )
            embed.set_footer(
                icon_url="https://i.imgur.com/0K0awOi.png",
                text=f"If this keeps happening, please contact {owner}",
            )
            await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        time2 = datetime.timedelta(seconds=math.ceil(error.retry_after))
        error = f"You are on cooldown. Try again after {humanize.precisedelta(time2)}"
        embed = discord.Embed(title="Too soon!",
                              description=error,
                              color=discord.Color.red())
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
        embed.set_footer(
            icon_url="https://i.imgur.com/0K0awOi.png",
            text=f"If you think this is a mistake, please contact {owner}",
        )
        await ctx.send(embed=embed)

    else:

        raise error
        embed = discord.Embed(
            title="Oh no!",
            description=
            (f"An error occurred. My developer has been notified of it, but if it continues to occur please DM {owner}"
             ),
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
          
          

if __name__ == "__main__":
    bot.run()
    if bot.hang:
        # We want to prevent this from finishing, but the bot is logged out
        while True:
            time.sleep(60)
