from dotenv.main import load_dotenv
import os

load_dotenv()

# Discord config
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
BOT_PREFIX = "!"

# Guild
GUILD_ID = int(os.getenv("GUILD_ID", ""))
