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


bot.run()
