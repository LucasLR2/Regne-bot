import os
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents (permisos de eventos de Discord)
import discord
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Crear instancia del bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Cargar módulos automáticamente
def load_cogs():
    bot.load_extension("modules.admin.admin")
    bot.load_extension("modules.bump_tracker.bump_tracker")
    bot.load_extension("modules.channel_control.channel_control")
    bot.load_extension("modules.economia.economia")
    bot.load_extension("modules.embeds.embed_commands")
    bot.load_extension("modules.users.user_commands")
    bot.load_extension("modules.roles.role_buttons")

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

if __name__ == "__main__":
    load_cogs()
    bot.run(TOKEN)
