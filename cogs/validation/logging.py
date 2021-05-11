import discord


async def log_problem(author: discord.Member, channel: discord.TextChannel, text: str):
    await channel.send(f"**Please double-check your post, {author.mention}!**\n{text}")
