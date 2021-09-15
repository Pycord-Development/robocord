import io
import os
import time
from abc import ABC
from functools import cached_property

import bftools
import discord
from discord.ext import commands
from dotenv import load_dotenv


class Bot(commands.Bot, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        load_dotenv()
        self.token = os.getenv("BOT_TOKEN")
        self.default_owner = os.getenv('OWNER_ID')
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ['JISHAKU_RETAIN'] = "True"
        self.owner_id = None
        self.owner_ids = [690420846774321221]
        self.load_extension('jishaku')
        self.brainfuck = bftools.BrainfuckTools()

    def run(self, *args, **kwargs):
        if len(args):
            super().run(*args, **kwargs)
        else:
            super().run(self.token, **kwargs)


def escape(text):
    return text.replace("`" * 3, "`​``")


def codeblock(code, lang="py"):
    return f"```{lang}\n{escape(code)}\n```"


def file(code, filename=None, ext="py"):
    if filename is None:
        filename = f"code.{ext}"
    data = io.BytesIO(bytes(code, encoding='utf8'))
    return discord.File(data, filename)


async def send_code(ctx, code, lang="py", filename=None, ext=None):
    cb = codeblock(code, lang=lang)
    if len(cb) < 500:  # max is 2000 but using 500 minimizes flood
        return await ctx.respond(cb, allowed_mentions=discord.AllowedMentions.none())
    else:
        if ext is None:
            ext = lang
        codefile = file(code, filename=filename, ext=ext)
        await ctx.send(file=codefile)
        await ctx.respond("Text was too long to put in a codeblock, used file instead")


class Timer:
    def __init__(self):
        self.start_time = time.perf_counter()
        self.end_time = None

    @cached_property
    def message(self):
        return f"Finished in {(self.duration * 1000):.0f}ms"

    @cached_property
    def duration(self):
        return self.end_time - self.start_time

    def finish(self):
        self.end_time = time.perf_counter()
        return self.duration
