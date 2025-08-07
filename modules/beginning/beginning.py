import discord
from discord.ext import commands

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="verify_setup")
    @commands.has_permissions(administrator=True)
    async def verify_setup(self, ctx):
        """Configura el sistema de verificación"""
        # ID del canal donde se enviará el mensaje de verificación
        verification_channel_id = 1400106792821981245
        verification_channel = self.bot.get_channel(verification_channel_id)
        
        if not verification_channel:
            await ctx.send("❌ No se pudo encontrar el canal **beginning**.")
            return
        
        # Crear el embed del mensaje de verificación
        embed = discord.Embed(
            title="🔐 Verificación del Servidor",
            description="¡Bienvenido a nuestro servidor!\n\n"
                       "Para acceder a todos los canales y participar en la comunidad, "
                       "necesitas verificarte primero.\n\n"
                       "**Haz clic en el botón de abajo para completar tu verificación** ⬇️",
            color=0x2b2d31
        )
        
        # Agregar la imagen del servidor (ícono del servidor)
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        # Agregar campos adicionales
        embed.add_field(
            name="📋 ¿Por qué verificarse?", 
            value="• Acceso completo al servidor\n• Participar en conversaciones\n• Unirte a eventos y actividades", 
            inline=False
        )
        
        embed.set_footer(
            text=f"Servidor: {ctx.guild.name} | Miembros: {ctx.guild.member_count}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        # Crear la vista con el botón
        view = VerificationView()
        
        # Enviar el mensaje al canal de verificación
        await verification_channel.send(embed=embed, view=view)
        
        # Confirmar al staff que se configuró correctamente
        await ctx.send(f"✅ Contenido enviado correctamente <#{verification_channel_id}>")
    
    @commands.command(name="rules_setup")
    @commands.has_permissions(administrator=True)
    async def rules_setup(self, ctx):
        """Envía las reglas del servidor al canal correspondiente"""
        # ID del canal de reglas
        rules_channel_id = 1400106792821981246
        rules_channel = self.bot.get_channel(rules_channel_id)
        
        if not rules_channel:
            await ctx.send("❌ No se pudo encontrar el canal de reglas.")
            return
        
        # Crear el embed de las reglas
        embed = discord.Embed(
            title="📜 Reglas del Servidor",
            description="¡Bienvenido/a! Este servidor te permite **ganar dinero, comprar productos y disfrutar de múltiples beneficios**. Para mantener un entorno seguro, justo y divertido para todos, es esencial respetar las siguientes normas:",
            color=0xe74c3c
        )
        
        # Agregar las reglas como campos
        embed.add_field(
            name="1. 🤝 Respeto ante todo",
            value="No se permite acoso, insultos, discriminación ni conductas tóxicas. Mantén un ambiente cordial y sano.",
            inline=False
        )
        
        embed.add_field(
            name="2. 🚫 Estafas terminantemente prohibidas",
            value="Cualquier intento de engañar, estafar o romper acuerdos será sancionado sin excepción.",
            inline=False
        )
        
        embed.add_field(
            name="3. 💼 Comercio con responsabilidad",
            value="Utiliza únicamente los canales habilitados para comprar o vender. Todo producto ofrecido debe ser legítimo. El servidor **no se hace responsable** por tratos fuera de los canales oficiales.",
            inline=False
        )
        
        embed.add_field(
            name="4. 💸 Sistema económico",
            value="No está permitido abusar del sistema, explotar errores o buscar ventajas injustas. Las recompensas pueden cambiar sin previo aviso según las decisiones del staff.",
            inline=False
        )
        
        embed.add_field(
            name="5. 📢 Sin spam ni publicidad externa",
            value="Está prohibido hacer spam, flood o promocionar servidores/productos sin autorización previa.",
            inline=False
        )
        
        embed.add_field(
            name="6. 🧠 Sentido común y respeto al staff",
            value="No suplantes al staff ni desafíes su autoridad. Ante dudas o problemas, repórtalo por los canales correspondientes.",
            inline=False
        )
        
        # Agregar advertencia final
        embed.add_field(
            name="🚨 Importante",
            value="El incumplimiento de estas normas puede resultar en **sanciones graves o permanentes**.\nAl permanecer en este servidor, **aceptas estas reglas**.",
            inline=False
        )
        
        # Agregar imagen del servidor
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        embed.set_footer(
            text=f"Reglas del servidor {ctx.guild.name}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        # Enviar las reglas al canal
        await rules_channel.send(embed=embed)
        
        # Confirmar al staff
        await ctx.send(f"✅ Contenido enviado correctamente <#{rules_channel_id}>")
    
    @commands.command(name="funcionamiento_setup")
    @commands.has_permissions(administrator=True)
    async def funcionamiento_setup(self, ctx):
        """Envía información sobre el funcionamiento de la tienda"""
        # ID del canal donde se enviará
        channel_id = 1400106793551663187
        channel = self.bot.get_channel(channel_id)
        
        if not channel:
            await ctx.send("❌ No se pudo encontrar el canal.")
            return
        
        # Crear el embed principal
        embed = discord.Embed(
            title="🛒 Funcionamiento de la Tienda",
            description="**Canal oficial:** <#1400106793551663189>\n\n"
                       "La tienda es el lugar donde puedes gastar el dinero que ganes dentro del servidor en objetos exclusivos, retiros, cuentas premium y más. A continuación, te explicamos cómo funciona:",
            color=0x3498db
        )
        
        # Sección: ¿Qué puedes comprar?
        embed.add_field(
            name="🎁 ¿Qué puedes comprar?",
            value="・**🎟️ Accesos a eventos especiales** Participa en dinámicas únicas desbloqueando objetos de entrada o participación.\n"
                  "・**💸 Retiros de dinero real** Canjea tu saldo acumulado por dinero real si cumples con los requisitos.\n"
                  "・**🧰 Ítems de uso personal** Cuentas premium como HBO, Spotify, Crunchyroll, entre otras. Solo tú podrás usarlas.\n"
                  "・**🎨 Cosméticos de perfil** Personaliza tu cuenta con marcos, insignias, colores, íconos y estilos únicos.\n"
                  "・**⏳ Objetos limitados** Artículos disponibles solo por tiempo limitado o en eventos específicos.",
            inline=False
        )
        
        # Sección: ¿Cómo ganar dinero?
        embed.add_field(
            name="💰 ¿Cómo ganar dinero?",
            value="Por ahora, la única forma de generar ingresos es a través de **reseñas**. **Canal:** <#1400106793551663190>\n\n"
                  "• Cuando estén disponibles, se anunciará allí mismo.\n"
                  "• Solo sigue las instrucciones y completa la reseña correctamente.\n"
                  "• Al hacerlo, recibirás una **recompensa en dinero real** acreditada a tu cuenta.",
            inline=False
        )
        
        # Consejo final
        embed.add_field(
            name="📌 Consejo",
            value="Ve a <#1403015632844488839> y ponte el rol <@&1400106792196898891> para recibir notificaciones cada vez que una reseña esté disponible.",
            inline=False
        )
        
        # Agregar imagen del servidor
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        embed.set_footer(
            text=f"Funcionamiento de economía {ctx.guild.name}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        # Enviar al canal
        await channel.send(embed=embed)
        
        # Confirmar al staff
        await ctx.send(f"✅ Contenido enviado correctamente <#{channel_id}>")
    
    @commands.command(name="autoroles_setup")
    @commands.has_permissions(administrator=True)
    async def autoroles_setup(self, ctx):
        """Configura el sistema de autoroles"""
        # ID del canal donde se enviará
        autoroles_channel_id = 1403015632844488839
        autoroles_channel = self.bot.get_channel(autoroles_channel_id)
        
        if not autoroles_channel:
            await ctx.send("❌ No se pudo encontrar el canal de autoroles.")
            return
        
        # Crear el embed del sistema de autoroles
        embed = discord.Embed(
            title="🎭 Sistema de Autoroles",
            description="¡Personaliza tu experiencia en el servidor! Selecciona los roles que más te interesen para recibir notificaciones específicas y acceder a funciones exclusivas.\n\n"
                       "**Haz clic en los botones de abajo para obtener o quitar tus roles:**",
            color=0x9b59b6
        )
        
        # Agregar información sobre cada rol
        embed.add_field(
            name="【📚 𝚁𝙴𝚂𝙴𝙽̃𝙰𝙳𝙾𝚁】",
            value="Recibe notificaciones cada vez que haya nuevas reseñas disponibles para completar y ganar dinero real.",
            inline=False
        )
        
        embed.add_field(
            name="【🚀 𝙱𝚄𝙼𝙿𝙴𝙰𝙳𝙾𝚁】", 
            value="Ayuda a hacer crecer el servidor y recibe notificaciones cuando sea momento de hacer bump en el servidor.",
            inline=False
        )
        
        # Agregar imagen del servidor
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)
        
        embed.set_footer(
            text=f"Autoroles de {ctx.guild.name}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        
        # Crear la vista con los botones de autoroles
        view = AutoRolesView()
        
        # Enviar el mensaje al canal de autoroles
        await autoroles_channel.send(embed=embed, view=view)
        
        # Confirmar al staff
        await ctx.send(f"✅ Contenido enviado correctamente <#{autoroles_channel_id}>")

class AutoRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Sin timeout para que los botones siempre funcionen
    
    @discord.ui.button(label="【📚 𝚁𝙴𝚂𝙴𝙽̃𝙰𝙳𝙾𝚁】", style=discord.ButtonStyle.blurple, custom_id="resenador_role")
    async def resenador_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ID del rol de reseñador
        role_id = 1400106792196898891
        role = interaction.guild.get_role(role_id)
        
        if not role:
            await interaction.response.send_message(
                "❌ Error: No se pudo encontrar el rol de Reseñador.", 
                ephemeral=True
            )
            return
        
        try:
            if role in interaction.user.roles:
                # Si el usuario ya tiene el rol, quitárselo
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"❌ Te has quitado el rol **{role.name}**. Ya no recibirás notificaciones de reseñas.",
                    ephemeral=True
                )
            else:
                # Si no tiene el rol, dárselo
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"✅ ¡Te has asignado el rol **{role.name}**! Ahora recibirás notificaciones cuando haya nuevas reseñas disponibles.",
                    ephemeral=True
                )
                
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Error: No tengo permisos para gestionar este rol.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error inesperado: {str(e)}", 
                ephemeral=True
            )
    
    @discord.ui.button(label="【🚀 𝙱𝚄𝙼𝙿𝙴𝙰𝙳𝙾𝚁】", style=discord.ButtonStyle.blurple, custom_id="bumpeador_role")
    async def bumpeador_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ID del rol de bumpeador
        role_id = 1400106792196898892
        role = interaction.guild.get_role(role_id)
        
        if not role:
            await interaction.response.send_message(
                "❌ Error: No se pudo encontrar el rol de Bumpeador.", 
                ephemeral=True
            )
            return
        
        try:
            if role in interaction.user.roles:
                # Si el usuario ya tiene el rol, quitárselo
                await interaction.user.remove_roles(role)
                await interaction.response.send_message(
                    f"❌ Te has quitado el rol **{role.name}**. Ya no recibirás notificaciones de bump.",
                    ephemeral=True
                )
            else:
                # Si no tiene el rol, dárselo
                await interaction.user.add_roles(role)
                await interaction.response.send_message(
                    f"✅ ¡Te has asignado el rol **{role.name}**! Ahora recibirás notificaciones para ayudar con el crecimiento del servidor.",
                    ephemeral=True
                )
                
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Error: No tengo permisos para gestionar este rol.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error inesperado: {str(e)}", 
                ephemeral=True
            )

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Sin timeout para que el botón siempre funcione
    
    @discord.ui.button(label="🔓 Verificarme", style=discord.ButtonStyle.green, emoji="✅")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ID del rol de verificado
        verified_role_id = 1400106792196898888
        # ID del canal de reglas
        rules_channel_id = 1400106792821981246
        
        # Obtener el rol de verificado
        verified_role = interaction.guild.get_role(verified_role_id)
        
        if not verified_role:
            await interaction.response.send_message(
                "❌ Error: No se pudo encontrar el rol de verificado.", 
                ephemeral=True
            )
            return
        
        # Verificar si el usuario ya tiene el rol
        if verified_role in interaction.user.roles:
            await interaction.response.send_message(
                "✅ Ya estás verificado.", 
                ephemeral=True
            )
            return
        
        try:
            # Asignar el rol de verificado
            await interaction.user.add_roles(verified_role)
            
            # Obtener el canal de reglas
            rules_channel = interaction.guild.get_channel(rules_channel_id)
            
            # Crear mensaje de bienvenida más elaborado
            welcome_embed = discord.Embed(
                title="🎉 ¡Verificación completada!",
                description=f"¡Bienvenido oficial a **{interaction.guild.name}**!\n\n"
                           f"✅ Has sido verificado correctamente y ahora tienes acceso completo al servidor.",
                color=0x00ff00
            )
            
            if rules_channel:
                welcome_embed.add_field(
                    name="📋 Próximos pasos",
                    value=f"• Lee nuestras reglas en {rules_channel.mention}\n"
                          f"• Explora los diferentes canales\n"
                          f"• ¡Preséntate con la comunidad!",
                    inline=False
                )
            
            # Agregar imagen del servidor
            if interaction.guild.icon:
                welcome_embed.set_thumbnail(url=interaction.guild.icon.url)
            
            welcome_embed.set_footer(
                text=f"¡Disfruta tu estancia en {interaction.guild.name}!",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            
            # Responder solo al usuario (ephemeral=True)
            await interaction.response.send_message(
                embed=welcome_embed,
                ephemeral=True
            )
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Error: No tengo permisos para asignar roles.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error inesperado: {str(e)}", 
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Verify(bot))