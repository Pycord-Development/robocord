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

@bot.user_command(name="Join Position")
async def _joinpos(ctx, member: discord.Member):
    all_members = list(ctx.guild.members)
    all_members.sort(key=lambda m: m.joined_at)

    def ord(n):
        return str(n) + ("th" if 4 <= n % 100 <= 20 else {
            1: "st",
            2: "nd",
            3: "rd"
        }.get(n % 10, "th"))

    embed = discord.Embed(
        title="Member info",
        description=
        f"{member.mention} was the {ord(all_members.index(member) + 1)} person to join",
    )
    await ctx.send(embed=embed)


MORSE_CODE_DICT = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    ", ": "--..--",
    ".": ".-.-.-",
    "?": "..--..",
    "/": "-..-.",
    "-": "-....-",
    "(": "-.--.",
    ")": "-.--.-",
    "!": "-.-.--",
    ",": "--..--",
}

# we make a list of what to replace with what


# Function to encrypt the string
# according to the morse code chart
def encrypt(message):
    cipher = ""
    for letter in message:
        if letter != " ":

            # Looks up the dictionary and adds the
            # correspponding morse code
            # along with a space to separate
            # morse codes for different characters
            cipher += MORSE_CODE_DICT[letter] + " "
        else:
            # 1 space indicates different characters
            # and 2 indicates different words
            cipher += " "

    return cipher


# Function to decrypt the string
# from morse to english
def decrypt(message):

    # extra space added at the end to access the
    # last morse code
    message += " "

    decipher = ""
    citext = ""
    for letter in message:

        # checks for space
        if letter != " ":

            # counter to keep track of space
            i = 0

            # storing morse code of a single character
            citext += letter

        # in case of space
        else:
            # if i = 1 that indicates a new character
            i += 1

            # if i = 2 that indicates a new word
            if i == 2:

                # adding space to separate words
                decipher += " "
            else:

                # accessing the keys using their values (reverse of encryption)
                decipher += list(MORSE_CODE_DICT.keys())[list(
                    MORSE_CODE_DICT.values()).index(citext)]
                citext = ""

    return decipher


@bot.message_command(name="Encrypt to Morse")
async def _tomorse(ctx, message: discord.message):
    result = encrypt(message.content.upper())
    await ctx.send(result)


@bot.message_command(name="Decrypt Morse")
async def _frommorse(ctx, message: discord.message):
    result = decrypt(message.content)
    await ctx.send(result)


@bot.message_command(name="Decrypt binary")
async def _frombinary(ctx, message: discord.message):

	if message.content.lower() == "01000000 01100101 01110110 01100101 01110010 01111001 01101111 01101110 01100101":
		await ctx.respond("SMH. Allowed mentions are turned off. go do something better.")
	else:
		a_binary_string = message.content
		binary_values = a_binary_string.split()

		ascii_string = ""
		for binary_value in binary_values:
			an_integer = int(binary_value, 2)

			ascii_character = chr(an_integer)

			ascii_string += ascii_character

		await ctx.send(ascii_string,
					allowed_mentions=discord.AllowedMentions.none())


@bot.message_command(name="Encrypt to binary")
async def _tobinary(ctx, message: discord.message):
	if message.content.lower() == 'bruce':
		await ctx.respond("01010000 01101111 01100111 01100111 01100101 01110010 01110011 00101110")
	elif message.content.lower() == 'easter egg':
		await ctx.respond("01010000 01110010 01101111 01100010 01100001 01100010 01101100 01111001 00100000 01101110 01101111 01110100")

	elif message.content.lower() == '@everyone':
		await ctx.respond("Wow, you though allowed mentions were on? Smh.")
	else:
		a_string = message.content
		a_byte_array = bytearray(a_string, "utf8")
		byte_list = []

		for byte in a_byte_array:
			binary_representation = bin(byte)
			byte_list.append(binary_representation)

		await ctx.send(" ".join(byte_list))


# ------
# Commented because max commands reached
# ------

# @bot.slash_command(name="Decrypt from hex", guild_ids=[869782707226439720, 881207955029110855])
# async def _fromhex(ctx, message:discord.message):
# 	hex_string = message.content[2:]

# 	bytes_object = bytes.fromhex(hex_string)

# 	ascii_string = bytes_object.decode("ASCII")

# 	await ctx.send(ascii_string)

# @bot.message_command(name="Encrypt to hex")
# async def _tohex(ctx, message:discord.message):
# 	hex_string = message.content
# 	an_integer = int(hex_string, 16)
# 	hex_value = hex(an_integer)
# 	await ctx.send(hex_value)


@bot.user_command(name="Avatar")
async def _avatar(ctx, member: discord.Member):
    embed = discord.Embed(
        title=f"{member}'s avatar!",
        description=f"[Link]({member.avatar.url})",
        color=member.color,
    )
    try:
        embed.set_image(url=member.avatar.url)
    except AttributeError:
        embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


binary = bot.command_group("binary", "Set of tools for converting binary")


@binary.command(name="encrypt")
async def binary_encrypt(ctx,
                         text: Option(
                             str, "The string you want to convert to binary")):
    a_string = text
    a_byte_array = bytearray(a_string, "utf8")
    byte_list = []

    for byte in a_byte_array:
        binary_representation = bin(byte)
        byte_list.append(binary_representation[2:])

    await ctx.send(" ".join(byte_list))


@binary.command(name="decrypt")
async def binary_decrypt(
    ctx, text: Option(str, "The binary string you want to decrypt")):
    a_binary_string = text
    binary_values = a_binary_string.split()

    ascii_string = ""
    for binary_value in binary_values:
        an_integer = int(binary_value, 2)

        ascii_character = chr(an_integer)

        ascii_string += ascii_character

    await ctx.send(ascii_string,
                   allowed_mentions=discord.AllowedMentions.none())

slowmode = bot.command_group(name='slowmode', description="Slowmode related commands for moderators")

@slowmode.command(name='set', description='Set the slowmode of the current channel')
@commands.has_role(881407111211384902)
async def set(ctx, time:Option(int, 'Enter the time in seconds')):
	if time > 21600:
		await ctx.respond(content=f"Slowmode of a channel must be {humanize.precisedelta(21600)} (21600 seconds) or less.", ephemeral=True)
	else:
		await ctx.channel.edit(slowmode_delay=time)
		await ctx.respond(f"The slowmode of this channel has been changed to {humanize.precisedelta(time)} ({time}s)")

@slowmode.command(name='off', description='Remove the slowmode from the current channel')
@commands.has_role(881407111211384902)
async def off(ctx):
	if ctx.channel.slowmode_delay == 0:
		await ctx.respond(content="This channel doesn't have a slowmode. Use `/slowmode set` to set a slowmode.", ephemeral=True)
	await ctx.channel.edit(slowmode_delay=0)
	await ctx.respond("Removed the slowmode from this channel!")
          

if __name__ == "__main__":
    bot.run()
    if bot.hang:
        # We want to prevent this from finishing, but the bot is logged out
        while True:
            time.sleep(60)
