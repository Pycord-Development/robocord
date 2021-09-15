import discord
from discord.app import Option

from tools import Bot, send_code

bot = Bot(command_prefix=';', intents=discord.Intents.all())

brainfuck = bot.command_group("bf", "Commands related to brainfuck.", guild_ids=[881207955029110855])


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


@bot.event
async def on_ready():
    print("ready")


bot.run()
