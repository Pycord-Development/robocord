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
import time

import discord
from discord.app import Option

from tools import Bot, send_code, get_prefix

bot = Bot(command_prefix=get_prefix,
          intents=discord.Intents.all(),
          activity=discord.Activity(type=discord.ActivityType.watching, name="Pycord"),
          description="The official pycord bot")

brainfuck = bot.command_group("bf", "Commands related to brainfuck.")
github = bot.command_group("github", "Commands related to github.")

repo = 'https://github.com/Pycord-Development/pycord'

for cog in bot.config.get('cogs', []):
    try:
        bot.load_extension(f"cogs.{cog}")
        print(cog)
    except discord.DiscordException:
        if __name__ == "__main__":
            print(f'!!! {cog} !!!')
        else:
            raise


@brainfuck.command()
async def encode(ctx, text: Option(str, "Text to encode in brainfuck")):
    """Encode text into brainfuck"""
    encoded = bot.brainfuck.encode(text)
    await send_code(ctx, encoded.code, lang="bf")


@brainfuck.command(name="compile")
async def _compile(ctx, code: Option(str, "Brainfuck code to compile into python")):
    """Compile brainfuck into python"""
    compiled = bot.brainfuck.compile(code)
    await send_code(ctx, compiled.code, lang="py")


@brainfuck.command()
async def decode(ctx, code: Option(str, "Brainfuck code to decode into text")):
    """Decode brainfuck into text"""
    decoded = bot.brainfuck.decode(code)
    await send_code(ctx, decoded.text, lang="txt", filename="text.txt")


@bot.slash_command()
async def invite(ctx):
    """Invite me to your server"""
    permissions = 2134207679
    url = discord.utils.oauth_url(client_id=bot.user.id, permissions=discord.Permissions(permissions=permissions),
                                  scopes=("bot", "applications.commands"))
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Invite", url=url))
    await ctx.respond("I'm glad you want to add me to your server, here's a link!", view=view)


@bot.slash_command()
async def ping(ctx):
    """Get the latency of the bot"""
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
    """View an issue from the pycord github repo"""
    url = f"{repo}/issues/{number}"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="View Issue", url=url))
    await ctx.respond(f"Here's a link", view=view)


@github.command()
async def pr(ctx, number: Option(int, "Pull request number")):
    """View a pull request from the pycord github repo"""
    url = f"{repo}/pulls/{number}"
    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="View Pull Request", url=url))
    await ctx.respond(f"Here's a link", view=view)


@bot.event
async def on_ready():
    print("ready")


@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:  # invoke the command again on edit
        if not after.author.bot:
            ctx = await bot.get_context(after)
            await bot.invoke(ctx)


if __name__ == "__main__":
    bot.run()
    if bot.hang:
        # We want to prevent this from finishing, but the bot is logged out
        while True:
            time.sleep(60)
