import discord
from discord.ext import commands
from datetime import datetime, timezone
import random
import aiohttp
from PIL import Image, ImageDraw
import io
import os

# Configuración de canales
WELCOME_CHANNEL_ID = 1400106792821981247  # ID del canal de bienvenida específico
GENERAL_CHANNEL_ID = 1400106792821981253   # ID del canal general

class WelcomeSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Lista de mensajes de bienvenida aleatorios
        self.welcome_messages = [
            "Te damos la bienvenida! Esperamos que hayas traído pizza. 🍕",
            "¡Un nuevo aventurero se ha unido a nosotros! 🎉",
            "¡Bienvenido/a! Que comience la diversión. 🎊",
            "¡Genial! Otro miembro increíble se ha unido. ✨",
            "¡Hola! Espero que te sientas como en casa. 🏠",
            "¡Bienvenido/a al mejor servidor de Discord! 🌟",
            "¡Un nuevo amigo ha llegado! ¡Dale la bienvenida! 👋"
        ]
        
        # Ruta de la imagen de fondo específica
        self.background_image = "resources/images/welcome.png"
        self.background_dir = "resources/images"
        
        # Crear directorio si no existe
        os.makedirs(self.background_dir, exist_ok=True)
        
        # ═══ CONFIGURACIÓN DE AVATAR ═══
        # Tamaño del avatar (en píxeles)
        self.avatar_size = 200
        
        # Posición del avatar
        self.avatar_position = "center"  # "center", "top", "bottom", "custom"
        
        # Para posición personalizada
        self.avatar_x_offset = 0  # Desplazamiento horizontal
        self.avatar_y_offset = 0  # Desplazamiento vertical
        
        # Configuración del borde del avatar
        self.avatar_border_size = 0  # Tamaño del borde en píxeles (0 para sin borde)
        self.avatar_border_color = (255, 255, 255, 255)

    async def download_avatar(self, user):
        """Descarga el avatar del usuario"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(str(user.display_avatar.url)) as response:
                    if response.status == 200:
                        return await response.read()
                    return None
        except Exception as e:
            print(f"❌ Error descargando avatar: {e}")
            return None

    def create_circular_avatar(self, avatar_bytes, size=None):
        """Crea un avatar circular con borde configurable"""
        if size is None:
            size = self.avatar_size
            
        try:
            avatar = Image.open(io.BytesIO(avatar_bytes))
            avatar = avatar.convert("RGBA")
            avatar = avatar.resize((size, size), Image.Resampling.LANCZOS)
            
            # Crear máscara circular
            mask = Image.new("L", (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            
            # Crear imagen circular
            output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            output.paste(avatar, (0, 0))
            output.putalpha(mask)
            
            # Agregar borde si está configurado
            if self.avatar_border_size > 0:
                border_size = self.avatar_border_size
                bordered_size = size + (border_size * 2)
                bordered = Image.new("RGBA", (bordered_size, bordered_size), (0, 0, 0, 0))
                
                # Dibujar círculo de borde
                draw_border = ImageDraw.Draw(bordered)
                draw_border.ellipse([0, 0, bordered_size-1, bordered_size-1], 
                                  fill=self.avatar_border_color, outline=self.avatar_border_color)
                
                # Pegar avatar encima del borde
                bordered.paste(output, (border_size, border_size), output)
                return bordered
            
            return output
            
        except Exception as e:
            print(f"❌ Error creando avatar circular: {e}")
            return None

    def calculate_avatar_position(self, bg_width, bg_height, avatar_width, avatar_height):
        """Calcula la posición del avatar según la configuración"""
        if self.avatar_position == "center":
            x = (bg_width - avatar_width) // 2
            y = (bg_height - avatar_height) // 2
        elif self.avatar_position == "top":
            x = (bg_width - avatar_width) // 2
            y = avatar_height // 2
        elif self.avatar_position == "bottom":
            x = (bg_width - avatar_width) // 2
            y = bg_height - avatar_height - (avatar_height // 2)
        elif self.avatar_position == "custom":
            center_x = (bg_width - avatar_width) // 2
            center_y = (bg_height - avatar_height) // 2
            x = center_x + self.avatar_x_offset
            y = center_y + self.avatar_y_offset
        else:
            x = (bg_width - avatar_width) // 2
            y = (bg_height - avatar_height) // 2
        
        # Asegurar que el avatar no se salga de la imagen
        x = max(0, min(x, bg_width - avatar_width))
        y = max(0, min(y, bg_height - avatar_height))
        
        return x, y

    async def create_welcome_image(self, member):
        """Crea una imagen de bienvenida con avatar superpuesto"""
        try:
            # Verificar que existe la imagen de fondo
            if not os.path.exists(self.background_image):
                print(f"⚠️ Imagen de fondo no encontrada: {self.background_image}")
                return None
            
            # Cargar imagen de fondo
            background = Image.open(self.background_image).convert("RGBA")
            
            # Redimensionar fondo si es muy grande
            bg_width, bg_height = background.size
            if bg_width > 1000:
                ratio = 1000 / bg_width
                new_height = int(bg_height * ratio)
                background = background.resize((1000, new_height), Image.Resampling.LANCZOS)
                bg_width, bg_height = background.size
            
            # Descargar avatar del usuario
            avatar_bytes = await self.download_avatar(member)
            if not avatar_bytes:
                print(f"⚠️ No se pudo descargar el avatar de {member.display_name}")
                return None
            
            # Crear avatar circular con tamaño configurado
            avatar_size = self.avatar_size
            avatar = self.create_circular_avatar(avatar_bytes, size=avatar_size)
            
            if not avatar:
                return None
            
            # Calcular posición del avatar
            avatar_x, avatar_y = self.calculate_avatar_position(bg_width, bg_height, avatar.width, avatar.height)
            
            # Pegar avatar en la posición calculada
            background.paste(avatar, (avatar_x, avatar_y), avatar)
            
            # Convertir a bytes para enviar
            img_bytes = io.BytesIO()
            background.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes
            
        except Exception as e:
            print(f"❌ Error creando imagen de bienvenida: {e}")
            return None

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Evento que se ejecuta cuando un nuevo miembro se une al servidor"""
        await self.send_welcome_message(member)
        await self.send_general_welcome(member)

    async def send_welcome_message(self, member):
        """Envía mensaje de bienvenida con imagen personalizada"""
        channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        if not channel:
            print(f"❌ Canal de bienvenida {WELCOME_CHANNEL_ID} no encontrado")
            return
        
        # Seleccionar mensaje aleatorio
        welcome_text = random.choice(self.welcome_messages)
        
        # Crear imagen personalizada con avatar superpuesto
        welcome_image = await self.create_welcome_image(member)
        
        embed = discord.Embed(
            title=f"¡Bienvenido/a {member.display_name}! 🎉",
            description=welcome_text,
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        try:
            if welcome_image:
                # Enviar imagen personalizada con avatar superpuesto
                file = discord.File(welcome_image, filename="welcome.png")
                embed.set_image(url="attachment://welcome.png")
                await channel.send(embed=embed, file=file)
                print(f"✅ Bienvenida con imagen personalizada enviada para {member.display_name}")
            else:
                # Fallback: imagen de fondo sin avatar superpuesto
                if os.path.exists(self.background_image):
                    with open(self.background_image, 'rb') as f:
                        file = discord.File(f, filename="welcome_bg.png")
                        embed.set_image(url="attachment://welcome_bg.png")
                        embed.set_thumbnail(url=member.display_avatar.url)
                        await channel.send(embed=embed, file=file)
                        print(f"✅ Bienvenida básica enviada para {member.display_name}")
                else:
                    # Último fallback: solo avatar
                    embed.set_image(url=member.display_avatar.url)
                    await channel.send(embed=embed)
                    print(f"✅ Bienvenida simple enviada para {member.display_name}")
            
        except Exception as e:
            print(f"❌ Error enviando mensaje de bienvenida: {e}")
            # Último fallback silencioso
            embed.set_thumbnail(url=member.display_avatar.url)
            await channel.send(embed=embed)

    async def send_general_welcome(self, member):
        """Envía embed simple al canal general"""
        channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
        if not channel:
            print(f"❌ Canal general {GENERAL_CHANNEL_ID} no encontrado")
            return
        
        embed = discord.Embed(
            description=f"{member.mention} *se ha unido al servidor, denle la bienvenida*",
            color=0x5865f2
        )
        
        try:
            await channel.send(embed=embed)
            print(f"✅ Mensaje general enviado para {member.display_name}")
        except Exception as e:
            print(f"❌ Error enviando mensaje general: {e}")

    @commands.command(name="welcome_test")
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx):
        """Prueba el sistema de bienvenida con el usuario actual"""
        await ctx.send("🧪 Probando sistema de bienvenida...")
        await self.send_welcome_message(ctx.author)
        await self.send_general_welcome(ctx.author)
        await ctx.send("✅ Test de bienvenida completado. Revisa los canales configurados.")

    @commands.command(name="welcome_config")
    @commands.has_permissions(administrator=True)
    async def welcome_config(self, ctx):
        """Muestra la configuración actual del sistema de bienvenida"""
        welcome_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        general_channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
        background_exists = os.path.exists(self.background_image)
        
        embed = discord.Embed(
            title="⚙️ Configuración de Bienvenida",
            color=0x00ffff,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="🎉 Canal de Bienvenida",
            value=welcome_channel.mention if welcome_channel else "❌ No encontrado",
            inline=False
        )
        
        embed.add_field(
            name="💬 Canal General",
            value=general_channel.mention if general_channel else "❌ No encontrado",
            inline=False
        )
        
        embed.add_field(
            name="🖼️ Imagen de Fondo",
            value=f"📁 Archivo: `{self.background_image}`\n{'✅ Encontrada' if background_exists else '❌ No encontrada'}",
            inline=False
        )
        
        embed.add_field(
            name="🎨 Configuración de Avatar",
            value=f"📏 Tamaño: {self.avatar_size}px\n📍 Posición: {self.avatar_position}\n🖼️ Borde: {self.avatar_border_size}px {'✅' if self.avatar_border_size > 0 else '❌'}",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Comandos",
            value="`!welcome_test` - Probar sistema\n`!welcome_config` - Ver configuración\n`!welcome_avatar` - Configurar avatar",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="welcome_avatar")
    @commands.has_permissions(administrator=True)
    async def configure_avatar(self, ctx, setting=None, *, value=None):
        """Configura el avatar superpuesto"""
        if not setting:
            embed = discord.Embed(
                title="🎨 Configuración de Avatar",
                color=0x00ffff,
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(name="📏 Tamaño", value=f"`{self.avatar_size}` píxeles", inline=True)
            embed.add_field(name="📍 Posición", value=f"`{self.avatar_position}`", inline=True)
            embed.add_field(name="🖼️ Borde", value=f"`{self.avatar_border_size}px`", inline=True)
            
            if self.avatar_position == "custom":
                embed.add_field(
                    name="📐 Offset personalizado",
                    value=f"X: `{self.avatar_x_offset}`, Y: `{self.avatar_y_offset}`",
                    inline=False
                )
            
            embed.add_field(
                name="💡 Comandos disponibles",
                value="`!welcome_avatar size <píxeles>`\n`!welcome_avatar position <center|top|bottom|custom>`\n`!welcome_avatar offset <x> <y>`\n`!welcome_avatar border <píxeles>`",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
        
        setting = setting.lower()
        
        if setting == "size":
            if not value:
                await ctx.send("❌ Usa: `!welcome_avatar size <número>`")
                return
            try:
                new_size = int(value)
                if 50 <= new_size <= 500:
                    self.avatar_size = new_size
                    await ctx.send(f"✅ Tamaño de avatar cambiado a **{new_size}px**")
                else:
                    await ctx.send("❌ El tamaño debe estar entre 50 y 500 píxeles")
            except ValueError:
                await ctx.send("❌ Usa: `!welcome_avatar size <número>`")
        
        elif setting == "position":
            positions = ["center", "top", "bottom", "custom"]
            if value and value.lower() in positions:
                self.avatar_position = value.lower()
                await ctx.send(f"✅ Posición cambiada a **{value.lower()}**")
            else:
                await ctx.send(f"❌ Posiciones válidas: {', '.join(positions)}")
        
        elif setting == "offset":
            if self.avatar_position != "custom":
                await ctx.send("❌ Los offsets solo funcionan con posición 'custom'")
                return
            if not value:
                await ctx.send("❌ Usa: `!welcome_avatar offset <x> <y>`")
                return
            try:
                offsets = value.split()
                if len(offsets) == 2:
                    x_offset = int(offsets[0])
                    y_offset = int(offsets[1])
                    if -300 <= x_offset <= 300 and -300 <= y_offset <= 300:
                        self.avatar_x_offset = x_offset
                        self.avatar_y_offset = y_offset
                        await ctx.send(f"✅ Offset cambiado a X:**{x_offset}**, Y:**{y_offset}**")
                    else:
                        await ctx.send("❌ Los offsets deben estar entre -300 y 300")
                else:
                    await ctx.send("❌ Usa: `!welcome_avatar offset <x> <y>`")
            except ValueError:
                await ctx.send("❌ Usa números válidos: `!welcome_avatar offset <x> <y>`")
        
        elif setting == "border":
            if not value:
                await ctx.send("❌ Usa: `!welcome_avatar border <número>`")
                return
            try:
                border_size = int(value)
                if 0 <= border_size <= 20:
                    self.avatar_border_size = border_size
                    await ctx.send(f"✅ Borde cambiado a **{border_size}px**")
                else:
                    await ctx.send("❌ El borde debe estar entre 0 y 20 píxeles")
            except ValueError:
                await ctx.send("❌ Usa: `!welcome_avatar border <número>`")
        
        else:
            await ctx.send("❌ Configuración no válida. Usa `!welcome_avatar` para ver opciones.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("[WelcomeSystem] Sistema de bienvenida listo (Con avatar superpuesto)")
        
        welcome_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
        general_channel = self.bot.get_channel(GENERAL_CHANNEL_ID)
        
        if not welcome_channel:
            print(f"⚠️ Canal de bienvenida {WELCOME_CHANNEL_ID} no encontrado")
        if not general_channel:
            print(f"⚠️ Canal general {GENERAL_CHANNEL_ID} no encontrado")
        
        if not os.path.exists(self.background_dir):
            print(f"⚠️ Directorio {self.background_dir} no encontrado, creándolo...")
            os.makedirs(self.background_dir, exist_ok=True)
        
        if os.path.exists(self.background_image):
            print(f"✅ Imagen de fondo encontrada: {self.background_image}")
        else:
            print(f"⚠️ Imagen de fondo no encontrada: {self.background_image}")
            print("💡 Tip: Coloca tu imagen welcome.png en resources/images/")

async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeSystem(bot))