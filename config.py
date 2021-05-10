from dotenv.main import load_dotenv
import os

load_dotenv()

# Discord config
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
BOT_PREFIX = ">"

GUILD_ID = int(os.getenv("GUILD", ""))

GIVE_AND_TAKE_CHANNEL = int(os.getenv("GIVE_AND_TAKE_CHANNEL", ""))

GIVE_AND_TAKE_CHAT_CHANNEL = int(os.getenv("GIVE_AND_TAKE_CHAT_CHANNEL", ""))
