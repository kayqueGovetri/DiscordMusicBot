import os
from dotenv import load_dotenv
from bot import Bot

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = Bot()
bot.run(TOKEN)
