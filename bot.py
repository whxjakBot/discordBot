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

# Configurar intents
intents = discord.Intents.all()

# Crear instancia del bot
bot = commands.Bot(command_prefix='.', intents=intents)

# Eliminar el comando help por defecto (opcional)
bot.remove_command("help")

# Lista de extensiones (cogs) a cargar
initial_extensions = [
    'cogs.help',
    'cogs.legit',
    'cogs.seguridad'
]

# Cargar extensiones
async def load_extensions():
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f'✅ Extensión cargada: {extension}')
        except Exception as e:
            print(f'❌ Error al cargar {extension}: {e}')

# Evento on_ready
@bot.event
async def on_ready():
    print(f'🤖 Bot conectado como {bot.user}')

# keep_alive para Render
from keep_alive import keep_alive

# Función principal
async def main():
    keep_alive()  # mantener activo el bot en Render
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

# Ejecutar el bot
asyncio.run(main())