import config
import discord
from discord.ext import commands

from .validation import validate_last_message


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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """When a message is received in the channel"""
        if message.channel != self.__channel:
            return
        await validate_last_message(message, self.__channel, self.__chat, self.__bot)

    @commands.Cog.listener()
    async def on_message_edit(self, _, message: discord.Message):
        """When last message is edited in the channel"""
        if message.channel != self.__channel:
            return
        await validate_last_message(message, self.__channel, self.__chat, self.__bot)


def setup(bot):
    bot.add_cog(Validation(bot))
