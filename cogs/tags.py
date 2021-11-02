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
from discord.ext import commands
from tools import Tag, Lowercase
import tortoise


def autocomplete_tag(owner=False, **kwargs):
    async def wrapper(interaction, value):
        kwargs['guild'] = interaction.guild.id
        if owner:
            if interaction.guild:
                if not interaction.author.guild_permissions.manage_messages:
                    kwargs['author'] = interaction.user.id
            else:
                kwargs['author'] = interaction.user.id

        return [tag.name for tag in await Tag.filter(name__istartswith=value, **kwargs).limit(25)]

    return wrapper


class Tags(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        # TODO: Rewrite this implementation once the library fully supports slash commands in cogs

        tags = bot.command_group("tags", "Tag editing commands")

        @tags.command()
        @discord.option("name", description="Name of the tag")
        @discord.option("content", description="Content of the tag")
        async def create(ctx, name: Lowercase, content):
            """
            Create a tag
            """
            if await Tag.exists(name=name):
                return await ctx.respond("That tag already exists!")
            if len(discord.utils.escape_markdown(content)) > 2000:
                return await ctx.respond("Content is too long!")

            guild_id = ctx.guild.id if ctx.guild else None

            await Tag.create(
                name=name,
                content=content,
                author=ctx.author.id,
                guild=guild_id
            )
            await ctx.respond(f"Tag `{name}` created successfully.")

        @tags.command()
        @discord.option("name", description="Name of the tag", autocomplete=autocomplete_tag())
        async def get(ctx, name: Lowercase):
            """
            Get a tag
            """
            await self.tag_get(ctx, name)

        @tags.command()
        @discord.option("name", description="Name of the tag", autocomplete=autocomplete_tag())
        async def delete(ctx, name: Lowercase):
            """
            Delete a tag
            """
            tag = await Tag.get(name=name)
            if not tag:
                return await ctx.respond("That tag doesn't exist!")
            if tag.author != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
                return await ctx.respond("You don't have permission to delete that tag!")
            await tag.delete()
            await ctx.respond(f"Tag `{name}` deleted successfully.")


        @tags.command()
        @discord.option("name", description="Name of the tag", autocomplete=autocomplete_tag())
        @discord.option("content", description="Content of the tag")
        async def edit(ctx, name: Lowercase, content):
            """
            Edit a tag
            """
            tag = await Tag.get(name=name)
            if not tag:
                return await ctx.respond("That tag doesn't exist!")
            if tag.author != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
                return await ctx.respond("You don't have permission to edit that tag!")
            if len(discord.utils.escape_markdown(content)) > 2000:
                return await ctx.respond("Content is too long!")

            await Tag.filter(name=name).update(content=content)
            await ctx.respond(f"Tag `{name}` edited successfully.")


    @staticmethod
    async def tag_get(ctx, name):
        try:
            tag = await Tag.get(name=name)
            await ctx.respond(tag.content)
        except tortoise.exceptions.DoesNotExist:
            await ctx.respond("That tag does not exist!")

    @discord.slash_command()
    @discord.option("name", description="Name of the tag", autocomplete=autocomplete_tag())
    async def tag(self, ctx, name: Lowercase):
        """
        Get a tag
        """
        await self.tag_get(ctx, name)


def setup(bot):
    bot.add_cog(Tags(bot))
