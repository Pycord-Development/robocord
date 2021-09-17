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
import collections
import copy
import io
import json
import os
import time
from abc import ABC
from functools import cached_property

import bftools
import discord
from discord.ext import commands
from dotenv import load_dotenv


class Config(collections.UserDict):
    def __init__(self, __dict, parent, **kwargs):
        self.parent = parent
        super().__init__(__dict, **kwargs)

    def __getitem__(self, key):
        return copy.deepcopy(super().__getitem__(key))

    def __setitem__(self, key, item):
        self._on_change()
        super().__setitem__(key, item)

    def __delitem__(self, key):
        self._on_change()
        super().__delitem__(key)

    def _on_change(self):
        self.parent.update_config()


class Storage:
    def __init__(self, storage_dir="storage"):
        self.storage_dir = storage_dir
        self.config = None
        if not os.path.exists(self.storage_dir):
            os.mkdir(self.storage_dir)
        if not os.path.exists(f"{self.storage_dir}/config.json"):
            open(f"{self.storage_dir}/config.json", "x")
            open(f"{self.storage_dir}/config.json", "w").write("{}")
        self.load_config()

    def load_config(self):
        with open(f"{self.storage_dir}/config.json", "r") as f:
            data = json.load(f)
            self.config = Config(data, self)
            return self.config

    def update_config(self):
        try:
            data = self.config.data
            with open(f"{self.storage_dir}/config.json", "w") as f:
                json.dump(data, f, indent=4)
        except AttributeError:
            pass


class Bot(commands.Bot, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        load_dotenv()
        self.token = os.getenv("BOT_TOKEN")
        self.default_owner = os.getenv('OWNER_ID')
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ['JISHAKU_RETAIN'] = "True"
        self.owner_id = None
        self.storage = Storage()
        self.owner_ids = self.config.get('owner_ids', [690420846774321221, 556119013298667520])
        self.load_extension('jishaku')
        self.brainfuck = bftools.BrainfuckTools()
        self.storage = Storage()
        self.hang = False

    @property
    def config(self):
        return self.storage.config

    def run(self, *args, **kwargs):
        if len(args):
            super().run(*args, **kwargs)
        else:
            super().run(self.token, **kwargs)


def escape(text):
    return text.replace("`" * 3, "`​``")


def codeblock(code, lang="py"):
    return f"```{lang}\n{escape(code)}\n```"


def codefile(code, filename=None, ext="py"):
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
        cf = codefile(code, filename=filename, ext=ext)
        await ctx.send(file=cf)
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


async def get_prefix(bot, message):
    # TODO: custom prefixes
    return commands.when_mentioned_or(bot.config.get('prefix', ';'))(bot, message)
