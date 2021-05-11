from cogs.validation.logging import log_problem
from .validation_error import ValidationError
import re
from typing import Annotated, List
import discord

choices = [
    "Anchovies",
    "Baby Corn",
    "Bacon",
    "Broccoli",
    "Cheese (plain)",
    "Cheese - Paneer",
    "Hard Cheese (Asiago/Parmesan/Romano)",
    "Chicken",
    "Egg",
    "Eggplant",
    "Ground Beef",
    "Ham",
    "Jalapeno",
    "Mushrooms",
    "Olives",
    "Onion",
    "Bell Pepper",
    "Pepperoncini",
    "Pepperoni",
    "Pineapple",
    "Potatoes",
    "Prosciutto",
    "Roasted Garlic",
    "Sausage",
    "Shrimp",
    "Spinach",
    "Tofu",
    "Tomatoes",
]


async def get_last_two_messages(
    channel: discord.TextChannel,
) -> Annotated[List[discord.Message], 2]:
    """Returns last message and second to last message that match pattern"""
    messages: List[discord.Message] = []
    async for message in channel.history(limit=20):
        content: str = message.content
        if re.search(r"[^-]+\s*[-]\s*\d+", content):
            messages += [message]
            if len(messages) == 2:
                return messages


def validate_sum(message: discord.Message):
    content: str = message.content
    lines = content.split("\n")
    total = 0
    for line in lines:
        match = re.search(r"([^-]+)\s*[-]\s*(\d+)", line)
        if not match:
            continue
        total += int(match.group(2))
    expected_total = len(choices) * 5
    if total != expected_total:
        raise ValidationError(
            f"Expected sum of all rankings to be {expected_total}, but got {total} instead.",
        )


def validate_plus_and_minus(message: discord.Message):
    content: str = message.content
    lines = content.split("\n")
    has_plus = False
    has_minus = False
    for line in lines:
        match = re.search(r"[^-]+\s*[-]\s*\d+[^+\-]*([+\-])", line)
        # line doesn't match pattern
        if not match:
            continue
        # group matched plus
        if match.group(1) == "+":
            if has_plus:
                raise ValidationError(f"Two plus signs found.")
            has_plus = True
            continue
        # group matched minus
        if has_minus:
            raise ValidationError(f"Two minus signs found.")
        has_minus = True
    if not has_plus:
        if not has_minus:
            raise ValidationError(f"Plus and minus signs are missing.")
        raise ValidationError(f"Plus sign is missing.")
    if not has_minus:
        raise ValidationError(f"Minus sign is missing.")


async def validate_last_message(
    message: discord.Message, channel: discord.TextChannel, chat: discord.TextChannel
):
    [last_message, previous_message] = await get_last_two_messages(channel)
    # skip validation if message does not match pattern
    if message != last_message:
        return
    # validate message
    try:
        validate_sum(message)
        validate_plus_and_minus(message)
    except ValidationError as error:
        await log_problem(message.author, chat, error.message)
