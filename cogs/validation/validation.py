import re
from typing import Annotated, Dict, List, Optional, Tuple

import discord
from cogs.validation.logging import log_death, log_problem
from discord.ext import commands
from fuzzywuzzy import process

from .validation_error import ValidationError

# Groups:
# 1: The name of the choice
# 2: The current number for the choice
# 3: '+', '-', or None
line_regex = re.compile(r"(\w[^-]*?)\s*[-]\s*(\d+)[^+\-]*([+\-])?")

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
        if line_regex.search(content):
            messages += [message]
            if len(messages) == 2:
                return messages


def validate_sum(message: discord.Message) -> int:
    """Throws ValidationError if the sum of rankings is not the expected amount
    Returns the number of ingredients in the list
    """
    content: str = message.content
    lines = content.split("\n")
    total = 0
    count = 0
    for line in lines:
        match = line_regex.search(line)
        if not match:
            continue
        total += int(match.group(2))
        count += 1
    expected_total = len(choices) * 5
    if total != expected_total:
        raise ValidationError(
            f"Expected sum of all rankings to be {expected_total}, but got {total} instead.",
        )
    return count


def validate_plus_and_minus(message: discord.Message):
    """Throws ValidationError if there are too many or too few pluses/minuses"""
    content: str = message.content
    lines = content.split("\n")
    has_plus = False
    has_minus = False
    for line in lines:
        match = line_regex.search(line)
        # line doesn't match pattern
        if not match or match.group(3) is None:
            continue
        # group matched plus
        if match.group(3) == "+":
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


def get_listed_choices(message: discord.Message) -> Dict[str, Tuple[int, str]]:
    content: str = message.content
    lines = content.split("\n")
    listed: Dict[str, Tuple[int, str]] = {}
    for line in lines:
        match = line_regex.search(line)
        # line doesn't match pattern
        if not match:
            continue
        choice_input = match.group(1)
        # find choice in list
        choice = process.extractOne(choice_input, choices)
        # check fuzz
        if not choice or choice[1] < 50:
            raise ValidationError(f"Didn't recognize the item '{choice_input}'.")
        listed[choice[0]] = (int(match.group(2)), match.group(3))
    return listed


def validate_choices(
    previous: discord.Message, message: discord.Message
) -> Optional[str]:
    """Check that choices are consistent with previous message
    Returns item that was killed if an item was killed this turn
    """
    death = None
    prev_list = get_listed_choices(previous)
    new_list = get_listed_choices(message)
    for item in prev_list.keys():
        prev_num = prev_list[item][0]
        # missing item
        if item not in new_list and prev_num > 0:
            raise ValidationError(f"Expected '{item}' but it is missing.")
        # item is missing but reached 0
        if item not in new_list:
            death = item
            continue
        # check valid numbers
        new_num, sign = new_list[item]
        if sign == "+" and new_num != prev_num + 1:
            raise ValidationError(f"{item} should be incremented to {prev_num + 1}.")
        if sign == "-" and new_num != prev_num - 1 and prev_num > 0:
            raise ValidationError(f"{item} should be decremented to {prev_num - 1}.")
        if sign is None and new_num != prev_num:
            raise ValidationError(f"{item} should still have the value {prev_num}.")
    return death


async def validate_last_message(
    message: discord.Message,
    channel: discord.TextChannel,
    chat: discord.TextChannel,
    bot: commands.Bot,
):
    [last_message, previous_message] = await get_last_two_messages(channel)
    # skip validation if message does not match pattern
    if message != last_message:
        return
    # validate message
    try:
        validate_plus_and_minus(message)
        death = validate_choices(previous_message, message)
        count = validate_sum(message)
        if death:
            await log_death(chat, death, count + 1)
        # success
        try:
            await message.remove_reaction("🚫", bot.user)
        except Exception:
            pass
        await message.add_reaction("✅")
    except ValidationError as error:
        # failure
        await message.add_reaction("🚫")
        await log_problem(message.author, chat, error.message)
