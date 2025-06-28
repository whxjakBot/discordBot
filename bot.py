import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

# Cargar variables del archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("❌ No se encontró la variable DISCORD_TOKEN en el archivo .env.")

# Crear instancia del bot
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

# Eliminar el comando help por defecto para evitar conflicto al cargar tu propio 'cogs.help'
bot.remove_command("help")

# Lista de extensiones (cogs) a cargar
initial_extensions = [
    'cogs.help',
    'cogs.legit',
    'cogs.seguridad'
]

# Función asincrónica para cargar extensiones
async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f'✅ Extensión cargada: {extension}')
        except Exception as e:
            print(f'❌ Error al cargar {extension}: {e}')

# Evento cuando el bot esté listo
@bot.event
async def on_ready():
    print(f'🤖 Bot conectado como {bot.user}')

# Función principal que ejecuta el bot
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

# Ejecutar el bot
asyncio.run(main())