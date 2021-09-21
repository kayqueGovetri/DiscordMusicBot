import os
from dotenv import load_dotenv
from bot import Bot

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)
bot = Bot()
bot.run(TOKEN)

# TODO Arrumar bug quando não é selecionado a música e o link do youtube.
