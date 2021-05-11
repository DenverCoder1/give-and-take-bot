from typing import List
import config
import discord
from discord.ext import commands

from .validation import get_killed_list, validate_last_message


class Validation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.__bot = bot
        self.__channel: discord.TextChannel
        self.__chat: discord.TextChannel

    @commands.Cog.listener()
    async def on_ready(self):
        """When bot is ready"""
        # get give and take channel objects
        self.__channel = self.__bot.get_channel(config.GIVE_AND_TAKE_CHANNEL)
        self.__chat = self.__bot.get_channel(config.GIVE_AND_TAKE_CHAT_CHANNEL)
        # check that channel exists
        assert isinstance(self.__channel, discord.TextChannel)
        assert isinstance(self.__chat, discord.TextChannel)
        # get pinned list of killed items
        self.__killed_list = await get_killed_list(self.__chat)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """When a message is received in the channel"""
        if message.channel != self.__channel:
            return
        await validate_last_message(
            message, self.__channel, self.__chat, self.__killed_list, self.__bot
        )

    @commands.Cog.listener()
    async def on_message_edit(self, _, message: discord.Message):
        """When last message is edited in the channel"""
        if message.channel != self.__channel:
            return
        await validate_last_message(
            message, self.__channel, self.__chat, self.__killed_list, self.__bot
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setkilled(self, ctx: commands.Context):
        """Set the killed list that is pinned by the bot
        ```
        >setkilled 15.) Mushrooms
        26.) Baby Corn
        27.) Ground Beef
        28.) Shrimp
        ```
        """
        # make sure it's the same guild as the command
        if ctx.message.guild != self.__killed_list.guild:
            return
        # remove comman part
        new_content = ctx.message.content.replace(ctx.prefix + ctx.invoked_with, "")
        # update killed list
        await self.__killed_list.edit(content=new_content.strip())


def setup(bot):
    bot.add_cog(Validation(bot))
