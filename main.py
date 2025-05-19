import discord
from discord.ext import commands, tasks
import os
import asyncio
from time import time
from dotenv import load_dotenv
from utils.bankconquista import desbloquear_conquista

# Carregar token do .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ID do dono
ID_DONO = 938195326140026920

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

# Criar bot
bot = commands.Bot(command_prefix=["-", "!"], intents=intents)

# Usuários em call
usuarios_em_call = {}

import os

async def carregar_cogs():
    for root, _, files in os.walk("cogs"):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                caminho = os.path.join(root, file).replace(os.sep, ".")[:-3]  # troca "/" por "." e remove ".py"
                try:
                    await bot.load_extension(caminho)
                    print(f"✅ Cog carregada: {caminho}")
                except Exception as e:
                    print(f"❌ Erro ao carregar {caminho}: {e}")


# Evento: mudança de estado de voz
@bot.event
async def on_voice_state_update(member, before, after):
    id_user = member.id

    if before.channel is None and after.channel is not None:
        usuarios_em_call[id_user] = int(time())

    elif before.channel is not None and after.channel is None:
        if id_user in usuarios_em_call:
            tempo = int(time()) - usuarios_em_call.pop(id_user, int(time()))
            if tempo > 0:
                print(f"[LOG] {member} ficou {tempo}s em call.")

# Loop: atualizar tempo de call (log simples)
@tasks.loop(seconds=60)
async def atualizar_tempo():
    agora = int(time())
    for id_user, entrada in usuarios_em_call.items():
        tempo = agora - entrada
        if tempo > 0:
            print(f"[LOOP] {id_user} +{tempo}s em call")

# Evento: detectar interação com o dono
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if ID_DONO in [u.id for u in message.mentions] or (
        message.reference and getattr(message.reference.resolved, "author", None) and
        message.reference.resolved.author.id == ID_DONO
    ):
        desbloqueou = desbloquear_conquista(message.author.id, "Falei com o Chefão")
        if desbloqueou:
            await message.channel.send(f"{message.author.mention} conquistou **Falei com o Chefão**!")

    await bot.process_commands(message)

# Evento: ao iniciar o bot
@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} online!")

    try:
        synced = await bot.tree.sync()
        print(f"📌 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"⚠️ Erro ao sincronizar comandos: {e}")

    atualizar_tempo.start()

# Comando manual de sincronização
@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Comandos sincronizados com sucesso!")

# Função principal
async def main():
    async with bot:
        await carregar_cogs()
        await bot.start(TOKEN)

# Iniciar
asyncio.run(main())
