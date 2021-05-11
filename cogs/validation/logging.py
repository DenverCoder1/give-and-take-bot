import discord
from utils.embedder import build_embed


async def log_problem(author: discord.Member, channel: discord.TextChannel, text: str):
    await channel.send(f"**Please double-check your post, {author.mention}!**\n{text}")


async def log_death(channel: discord.TextChannel, item: str, placement: int):
    await channel.send(embed=build_embed(f"🪦 RIP {item} (#{placement})"))
