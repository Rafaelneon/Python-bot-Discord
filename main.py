import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Evento on_ready, só um único
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user} e comandos sincronizados.")

# Função async para carregar cogs automaticamente, incluindo subpastas
async def load_cogs(bot):
    base_dir = "cogs"
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                relative_path = os.path.join(root, file).replace("\\", "/")  # Windows fix
                module = relative_path[:-3].replace("/", ".")
                try:
                    await bot.load_extension(module)
                    print(f"✅ Cog carregada: {module}")
                except Exception as e:
                    print(f"❌ Falha ao carregar {module}: {e}")

async def main():
    async with bot:
        await load_cogs(bot)
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
