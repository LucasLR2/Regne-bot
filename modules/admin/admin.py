import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ────────────────────────────────────────────────────────────
    # Comandos de moderación básica
    # ────────────────────────────────────────────────────────────
    
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason="No especificada"):
        """Expulsa a un miembro del servidor"""
        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="❌ Error",
                description="No puedes expulsar a alguien con un rol igual o superior al tuyo.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.kick(reason=f"Expulsado por {ctx.author} - {reason}")
            embed = discord.Embed(
                title="✅ Usuario expulsado",
                description=f"**{member.display_name}** ha sido expulsado del servidor.",
                color=0x00ff00
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Sin permisos",
                description="No tengo permisos para expulsar a este usuario.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason="No especificada"):
        """Banea a un miembro del servidor"""
        if member.top_role >= ctx.author.top_role:
            embed = discord.Embed(
                title="❌ Error",
                description="No puedes banear a alguien con un rol igual o superior al tuyo.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.ban(reason=f"Baneado por {ctx.author} - {reason}")
            embed = discord.Embed(
                title="🔨 Usuario baneado",
                description=f"**{member.display_name}** ha sido baneado del servidor.",
                color=0xff0000
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Sin permisos",
                description="No tengo permisos para banear a este usuario.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_member(self, ctx, user_id: int, *, reason="No especificada"):
        """Desbanea a un usuario por su ID"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=f"Desbaneado por {ctx.author} - {reason}")
            
            embed = discord.Embed(
                title="✅ Usuario desbaneado",
                description=f"**{user.display_name}** ha sido desbaneado del servidor.",
                color=0x00ff00
            )
            embed.add_field(name="Razón", value=reason, inline=False)
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Usuario no encontrado",
                description="No se encontró un usuario con esa ID o no está baneado.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Sin permisos",
                description="No tengo permisos para desbanear usuarios.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    # ────────────────────────────────────────────────────────────
    # Limpieza de mensajes
    # ────────────────────────────────────────────────────────────
    
    @commands.command(name="clear", aliases=["purge", "clean"])
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 10):
        """Elimina una cantidad específica de mensajes"""
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="❌ Cantidad inválida",
                description="Debes especificar un número entre 1 y 100.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 para incluir el comando
            embed = discord.Embed(
                title="🧹 Mensajes eliminados",
                description=f"Se eliminaron **{len(deleted) - 1}** mensajes.",
                color=0x00ff00
            )
            
            # Enviar confirmación y eliminarla después de 5 segundos
            confirmation = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await confirmation.delete()
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Sin permisos",
                description="No tengo permisos para eliminar mensajes.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

    # ────────────────────────────────────────────────────────────
    # Información del servidor
    # ────────────────────────────────────────────────────────────
    
    @commands.command(name="serverinfo")
    @commands.has_permissions(manage_guild=True)
    async def server_info(self, ctx):
        """Muestra información detallada del servidor"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 Información de {guild.name}",
            color=0x00ffff,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        # Información básica
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        embed.add_field(name="👑 Propietario", value=guild.owner.mention if guild.owner else "Desconocido", inline=True)
        embed.add_field(name="📅 Creado", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        
        # Estadísticas de miembros
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bots = sum(1 for member in guild.members if member.bot)
        
        embed.add_field(name="👥 Miembros totales", value=total_members, inline=True)
        embed.add_field(name="🟢 En línea", value=online_members, inline=True)
        embed.add_field(name="🤖 Bots", value=bots, inline=True)
        
        # Canales
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(name="💬 Canales de texto", value=text_channels, inline=True)
        embed.add_field(name="🔊 Canales de voz", value=voice_channels, inline=True)
        embed.add_field(name="📁 Categorías", value=categories, inline=True)
        
        # Roles y emojis
        embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="😀 Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="🚀 Boost Level", value=guild.premium_tier, inline=True)
        
        await ctx.send(embed=embed)

    # ────────────────────────────────────────────────────────────
    # Comandos de utilidad
    # ────────────────────────────────────────────────────────────
    
    @commands.command(name="userinfo")
    @commands.has_permissions(manage_guild=True)
    async def user_info(self, ctx, member: discord.Member = None):
        """Muestra información de un usuario"""
        if member is None:
            member = ctx.author
        
        embed = discord.Embed(
            title=f"👤 Información de {member.display_name}",
            color=member.color if member.color != discord.Color.default() else 0x00ffff,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Información básica
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="📛 Nombre", value=str(member), inline=True)
        embed.add_field(name="📅 Cuenta creada", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        
        # Información del servidor
        embed.add_field(name="📥 Se unió", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🎭 Rol más alto", value=member.top_role.mention, inline=True)
        embed.add_field(name="🤖 Es bot", value="Sí" if member.bot else "No", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="say")
    @commands.has_permissions(manage_messages=True)
    async def say_message(self, ctx, *, message):
        """Hace que el bot repita un mensaje"""
        await ctx.message.delete()  # Eliminar el comando
        await ctx.send(message)

    # ────────────────────────────────────────────────────────────
    # Comando de test para verificar que el módulo funciona
    # ────────────────────────────────────────────────────────────
    
    @commands.command(name="admin_test")
    @commands.has_permissions(administrator=True)
    async def admin_test(self, ctx):
        """Comando de prueba para administradores"""
        embed = discord.Embed(
            title="✅ Módulo Admin funcionando",
            description="El módulo de administración está cargado y funcionando correctamente.",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="📋 Comandos disponibles", value=
            "`!kick` - Expulsar usuario\n"
            "`!ban` - Banear usuario\n"
            "`!unban` - Desbanear usuario\n"
            "`!clear` - Limpiar mensajes\n"
            "`!serverinfo` - Info del servidor\n"
            "`!userinfo` - Info de usuario\n"
            "`!say` - Repetir mensaje",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print("[AdminCommands] Módulo de administración listo")

# Función setup requerida para cargar el cog
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))