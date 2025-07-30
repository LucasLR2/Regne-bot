import discord
from discord.ext import commands

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Placeholder - puedes agregar comandos aquí después
    @commands.command(name="economia_test")
    @commands.has_permissions(administrator=True)
    async def economia_test(self, ctx):
        """Comando de prueba para administradores"""
        embed = discord.Embed(
            title="✅ Módulo Economia funcionando",
            description="El módulo de economía está cargado correctamente.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economia(bot))