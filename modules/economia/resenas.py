import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
from typing import Dict, Set, Optional, List

class ResenasView(discord.ui.View):
    def __init__(self, resenas_disponibles: int, canal_resenas_id: int, staff_role_ids: List[int], mensaje_id: int = None):
        super().__init__(timeout=None)  # Sin timeout para que persista
        self.resenas_disponibles = resenas_disponibles
        self.resenas_originales = resenas_disponibles
        self.usuarios_con_resena: Set[int] = set()
        self.canal_resenas_id = canal_resenas_id
        self.staff_role_ids = staff_role_ids
        self.mensaje_id = mensaje_id
        
        # Configurar el botón inicial
        self.actualizar_boton()
    
    def actualizar_boton(self):
        """Actualiza el estado del botón según los cupos disponibles"""
        boton = self.children[0] if self.children else None
        
        if self.resenas_disponibles > 0:
            if boton:
                boton.label = "Quiero reseñas"
                boton.disabled = False
                boton.style = discord.ButtonStyle.primary
        else:
            if boton:
                boton.label = "Reseñas agotadas"
                boton.disabled = True
                boton.style = discord.ButtonStyle.secondary
    
    async def actualizar_mensaje_original(self, interaction: discord.Interaction):
        """Actualiza el mensaje original con el nuevo estado"""
        try:
            embed_actualizado = discord.Embed(
                title="📝 Sistema de Reseñas",
                description=f"Hay **{self.resenas_disponibles}** reseñas disponibles de **{self.resenas_originales}** totales.",
                color=0x0099ff
            )
            
            if self.resenas_disponibles > 0:
                embed_actualizado.add_field(
                    name="Estado", 
                    value="✅ Disponible", 
                    inline=True
                )
            else:
                embed_actualizado.add_field(
                    name="Estado", 
                    value="❌ Agotado", 
                    inline=True
                )
            
            embed_actualizado.add_field(
                name="Instrucciones", 
                value="Presiona el botón para solicitar una reseña", 
                inline=True
            )
            
            # Obtener el mensaje original y editarlo
            canal = interaction.guild.get_channel(self.canal_resenas_id)
            if canal and self.mensaje_id:
                try:
                    mensaje = await canal.fetch_message(self.mensaje_id)
                    await mensaje.edit(embed=embed_actualizado, view=self)
                except discord.NotFound:
                    # Si no se encuentra el mensaje, enviar uno nuevo
                    nuevo_mensaje = await canal.send(embed=embed_actualizado, view=self)
                    self.mensaje_id = nuevo_mensaje.id
                except discord.HTTPException:
                    pass  # Error al editar, continuar sin actualizar
            
        except Exception as e:
            print(f"Error al actualizar mensaje: {e}")
    
    @discord.ui.button(label="Quiero reseñas", style=discord.ButtonStyle.primary)
    async def solicitar_resena(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Maneja la solicitud de reseña cuando se presiona el botón"""
        
        # Verificar si el usuario ya tiene una reseña activa
        if interaction.user.id in self.usuarios_con_resena:
            embed = discord.Embed(
                title="⚠️ Reseña ya solicitada",
                description="Ya tienes una reseña en curso. No puedes solicitar otra hasta que se complete la actual.",
                color=0xff9900
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Verificar si aún hay cupos disponibles
        if self.resenas_disponibles <= 0:
            embed = discord.Embed(
                title="❌ Sin cupos disponibles",
                description="Ya no hay reseñas disponibles en este momento.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Defer la respuesta para tener más tiempo
            await interaction.response.defer(ephemeral=True)
            
            # Crear el canal de ticket
            guild = interaction.guild
            categoria = None  # Puedes especificar una categoría si quieres
            
            # Configurar permisos del canal
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    read_message_history=True
                ),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True,
                    embed_links=True
                )
            }
            
            # Agregar permisos para los roles de staff
            for role_id in self.staff_role_ids:
                staff_role = guild.get_role(role_id)
                if staff_role:
                    overwrites[staff_role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        read_message_history=True,
                        manage_messages=True
                    )
            
            # Crear el canal
            nombre_canal = f"resenas-{interaction.user.name}".replace(" ", "-").lower()
            # Limpiar caracteres especiales del nombre
            nombre_canal = ''.join(c for c in nombre_canal if c.isalnum() or c in '-_')
            
            canal_ticket = await guild.create_text_channel(
                name=nombre_canal,
                overwrites=overwrites,
                category=categoria,
                topic=f"Reseña para {interaction.user.display_name}"
            )
            
            # Crear menciones de los roles de staff
            menciones_staff = []
            for role_id in self.staff_role_ids:
                staff_role = guild.get_role(role_id)
                if staff_role:
                    menciones_staff.append(staff_role.mention)
            
            # Enviar mensaje inicial en el canal creado
            embed_bienvenida = discord.Embed(
                title="🎫 Canal de Reseña Creado",
                description="Gracias por tu interés. Por favor, aguarda a que un superior te atienda.",
                color=0x00ff00
            )
            embed_bienvenida.add_field(
                name="Usuario", 
                value=interaction.user.mention, 
                inline=True
            )
            embed_bienvenida.add_field(
                name="Creado", 
                value=f"<t:{int(interaction.created_at.timestamp())}:R>", 
                inline=True
            )
            
            # Mensaje con menciones
            mensaje_menciones = f"{interaction.user.mention}"
            if menciones_staff:
                mensaje_menciones += f" {' '.join(menciones_staff)}"
            
            await canal_ticket.send(mensaje_menciones, embed=embed_bienvenida)
            
            # Actualizar el estado
            self.resenas_disponibles -= 1
            self.usuarios_con_resena.add(interaction.user.id)
            
            # Actualizar el botón
            self.actualizar_boton()
            
            # Actualizar el mensaje original
            await self.actualizar_mensaje_original(interaction)
            
            # Responder al usuario
            embed_respuesta = discord.Embed(
                title="✅ Canal creado exitosamente",
                description=f"Se ha creado tu canal de reseña: {canal_ticket.mention}",
                color=0x00ff00
            )
            
            await interaction.followup.send(embed=embed_respuesta, ephemeral=True)
            
        except discord.Forbidden:
            embed_error = discord.Embed(
                title="❌ Error de permisos",
                description="No tengo permisos suficientes para crear canales.",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed_error, ephemeral=True)
        
        except Exception as e:
            embed_error = discord.Embed(
                title="❌ Error inesperado",
                description=f"Ocurrió un error al crear el canal: {str(e)}",
                color=0xff0000
            )
            await interaction.followup.send(embed=embed_error, ephemeral=True)

class Resenas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Almacenar las vistas activas para persistencia durante la sesión
        self.vistas_activas: Dict[int, ResenasView] = {}
        
        # 🔧 CONFIGURACIÓN MANUAL - CAMBIA ESTOS IDs POR LOS DE TU SERVIDOR
        self.CANAL_RESENAS_ID = 1400106793551663190  # ID del canal donde se publican las reseñas
        self.ROL_NOTIFICACION_RESENAS_ID = 1400106792196898891 # ID del rol que se menciona al usuario al publicar reseñas
        self.STAFF_ROLE_IDS = [
            1400106792280658070,  # ID del primer rol de staff/moderación
            1400106792196898889   # ID del segundo rol de staff/moderación
        ]
    
    @commands.command(name="resenas")
    @commands.has_permissions(administrator=True)
    async def comando_resenas(self, ctx, num_resenas: int):
        """
        Comando para administradores que inicia el sistema de reseñas
        
        Uso: !resenas <número>
        Ejemplo: !resenas 3
        """
        
        if num_resenas <= 0:
            embed_error = discord.Embed(
                title="❌ Número inválido",
                description="El número de reseñas debe ser mayor a 0.",
                color=0xff0000
            )
            await ctx.send(embed=embed_error)
            return
        
        if num_resenas > 50:  # Límite de seguridad
            embed_error = discord.Embed(
                title="❌ Número muy alto",
                description="Por seguridad, el máximo de reseñas es 50.",
                color=0xff0000
            )
            await ctx.send(embed=embed_error)
            return
        
        # Obtener el canal de reseñas
        canal_resenas = self.bot.get_channel(self.CANAL_RESENAS_ID)
        if not canal_resenas:
            embed_error = discord.Embed(
                title="❌ Canal no encontrado",
                description=f"No se pudo encontrar el canal con ID: {self.CANAL_RESENAS_ID}\n"
                           "Verifica que el ID sea correcto y que el bot tenga acceso.",
                color=0xff0000
            )
            await ctx.send(embed=embed_error)
            return
        
        # Verificar que los roles existan
        roles_validos = []
        for role_id in self.STAFF_ROLE_IDS:
            role = ctx.guild.get_role(role_id)
            if role:
                roles_validos.append(role)
        
        # Confirmar en el canal de administración
        embed_confirmacion = discord.Embed(
            title="✅ Sistema de reseñas iniciado",
            description=f"Se han configurado **{num_resenas}** reseñas disponibles.",
            color=0x00ff00
        )
        embed_confirmacion.add_field(
            name="Canal de publicación", 
            value=canal_resenas.mention, 
            inline=True
        )
        
        if roles_validos:
            roles_texto = ", ".join([role.mention for role in roles_validos])
            embed_confirmacion.add_field(
                name="Roles de staff", 
                value=roles_texto, 
                inline=True
            )
        else:
            embed_confirmacion.add_field(
                name="⚠️ Roles de staff", 
                value="No se encontraron roles válidos", 
                inline=True
            )
        
        await ctx.send(embed=embed_confirmacion)
        
        # Crear embed para el canal público
        embed_publico = discord.Embed(
            title="📝 Sistema de Reseñas",
            description=f"Hay **{num_resenas}** reseñas disponibles de **{num_resenas}** totales.",
            color=0x0099ff
        )
        embed_publico.add_field(
            name="Estado", 
            value="✅ Disponible", 
            inline=True
        )
        embed_publico.add_field(
            name="Instrucciones", 
            value="Presiona el botón para solicitar una reseña", 
            inline=True
        )
        
        # Enviar mensaje al canal público
        rol_notificacion = ctx.guild.get_role(self.ROL_NOTIFICACION_RESENAS_ID)
        mensaje_notificacion = ""
        if rol_notificacion:
            mensaje_notificacion = rol_notificacion.mention

        mensaje_publico = await canal_resenas.send(mensaje_notificacion, embed=embed_publico)
        
        # Crear y configurar la vista
        vista_resenas = ResenasView(num_resenas, self.CANAL_RESENAS_ID, self.STAFF_ROLE_IDS, mensaje_publico.id)
        self.vistas_activas[canal_resenas.id] = vista_resenas
        
        # Editar el mensaje para agregar la vista
        await mensaje_publico.edit(embed=embed_publico, view=vista_resenas)
    
    @commands.command(name="estado_resenas")
    @commands.has_permissions(administrator=True)
    async def estado_resenas(self, ctx):
        """
        Muestra el estado actual del sistema de reseñas
        """
        if not self.vistas_activas:
            embed = discord.Embed(
                title="📊 Estado del Sistema",
                description="No hay sesiones de reseñas activas.",
                color=0x999999
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📊 Estado del Sistema de Reseñas",
            color=0x0099ff
        )
        
        for canal_id, vista in self.vistas_activas.items():
            canal = self.bot.get_channel(canal_id)
            canal_nombre = canal.name if canal else f"Canal {canal_id}"
            
            embed.add_field(
                name=f"#{canal_nombre}",
                value=f"**Disponibles:** {vista.resenas_disponibles}/{vista.resenas_originales}\n"
                      f"**Usuarios activos:** {len(vista.usuarios_con_resena)}\n"
                      f"**Mensaje ID:** {vista.mensaje_id}",
                inline=True
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="cerrar_resena")
    @commands.has_permissions(manage_channels=True)
    async def cerrar_resena(self, ctx, usuario: discord.Member = None):
        """
        Cierra el canal de reseña de un usuario y lo libera del sistema
        
        Uso: !cerrar_resena @usuario
        Si se usa en un canal de reseña, detecta automáticamente al usuario
        """
        canal_actual = ctx.channel
        
        # Si no se especifica usuario, intentar detectar desde el nombre del canal
        if not usuario and canal_actual.name.startswith("resenas-"):
            nombre_usuario = canal_actual.name.replace("resenas-", "")
            for member in ctx.guild.members:
                if member.name.lower() == nombre_usuario.lower():
                    usuario = member
                    break
        
        if not usuario:
            embed_error = discord.Embed(
                title="❌ Usuario no especificado",
                description="Debes mencionar al usuario o usar el comando en su canal de reseña.",
                color=0xff0000
            )
            await ctx.send(embed=embed_error)
            return
        
        # Liberar al usuario de todas las vistas activas y actualizar mensajes
        usuario_liberado = False
        for vista in self.vistas_activas.values():
            if usuario.id in vista.usuarios_con_resena:
                vista.usuarios_con_resena.remove(usuario.id)
                usuario_liberado = True
                
                # Crear una interacción falsa para actualizar el mensaje
                class FakeInteraction:
                    def __init__(self, guild):
                        self.guild = guild
                
                fake_interaction = FakeInteraction(ctx.guild)
                await vista.actualizar_mensaje_original(fake_interaction)
        
        # Eliminar el canal si estamos en uno de reseñas
        if canal_actual.name.startswith("resenas-"):
            embed_cierre = discord.Embed(
                title="✅ Reseña completada",
                description=f"La reseña de {usuario.display_name} ha sido completada.",
                color=0x00ff00
            )
            await ctx.send(embed=embed_cierre)
            
            # Esperar un poco antes de eliminar el canal
            await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=3))
            await canal_actual.delete(reason=f"Reseña completada para {usuario.display_name}")
        else:
            if usuario_liberado:
                embed = discord.Embed(
                    title="✅ Usuario liberado",
                    description=f"{usuario.display_name} ha sido liberado del sistema de reseñas.",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Usuario no encontrado",
                    description=f"{usuario.display_name} no tenía reseñas activas.",
                    color=0xff9900
                )
            await ctx.send(embed=embed)
    
    @commands.command(name="reset_resenas")
    @commands.has_permissions(administrator=True)
    async def reset_resenas(self, ctx):
        """
        Resetea el sistema de reseñas, eliminando todas las vistas activas
        """
        self.vistas_activas.clear()
        
        embed = discord.Embed(
            title="🔄 Sistema reiniciado",
            description="Se han eliminado todas las sesiones de reseñas activas.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="actualizar_resenas")
    @commands.has_permissions(administrator=True)
    async def actualizar_resenas(self, ctx):
        """
        Fuerza la actualización de todos los mensajes de reseñas activos
        """
        if not self.vistas_activas:
            embed = discord.Embed(
                title="⚠️ Sin sistemas activos",
                description="No hay sistemas de reseñas activos para actualizar.",
                color=0xff9900
            )
            await ctx.send(embed=embed)
            return
        
        actualizados = 0
        for vista in self.vistas_activas.values():
            try:
                class FakeInteraction:
                    def __init__(self, guild):
                        self.guild = guild
                
                fake_interaction = FakeInteraction(ctx.guild)
                await vista.actualizar_mensaje_original(fake_interaction)
                actualizados += 1
            except Exception as e:
                print(f"Error actualizando vista: {e}")
        
        embed = discord.Embed(
            title="🔄 Actualización completada",
            description=f"Se actualizaron {actualizados} mensajes de reseñas.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="config_info")
    @commands.has_permissions(administrator=True)
    async def config_info(self, ctx):
        """
        Muestra la configuración actual del sistema
        """
        embed = discord.Embed(
            title="⚙️ Configuración del Sistema",
            color=0x0099ff
        )
        
        # Información del canal
        canal = self.bot.get_channel(self.CANAL_RESENAS_ID)
        embed.add_field(
            name="Canal de reseñas",
            value=f"{canal.mention if canal else 'No encontrado'} (ID: {self.CANAL_RESENAS_ID})",
            inline=False
        )
        
        # Información de roles
        roles_info = []
        for role_id in self.STAFF_ROLE_IDS:
            role = ctx.guild.get_role(role_id)
            if role:
                roles_info.append(f"{role.mention} (ID: {role_id})")
            else:
                roles_info.append(f"Rol no encontrado (ID: {role_id})")
        
        embed.add_field(
            name="Roles de staff",
            value="\n".join(roles_info) if roles_info else "No configurados",
            inline=False
        )
        
        # Estado del sistema
        embed.add_field(
            name="Sistemas activos",
            value=str(len(self.vistas_activas)),
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    # Comando de prueba mantenido
    @commands.command(name="resenas_test")
    @commands.has_permissions(administrator=True)
    async def resenas_test(self, ctx):
        """Comando de prueba para administradores"""
        embed = discord.Embed(
            title="✅ Módulo Resenas funcionando",
            description="El módulo de economía con sistema de reseñas está cargado correctamente.",
            color=0x00ff00
        )
        embed.add_field(
            name="Comandos disponibles",
            value="`!resenas <num>` - Iniciar sistema de reseñas\n"
                  "`!estado_resenas` - Ver estado actual\n"
                  "`!cerrar_resena @usuario` - Cerrar reseña\n"
                  "`!reset_resenas` - Reiniciar sistema\n"
                  "`!actualizar_resenas` - Forzar actualización\n"
                  "`!config_info` - Ver configuración actual",
            inline=False
        )
        await ctx.send(embed=embed)
    
    # Manejo de errores
    @comando_resenas.error
    async def resenas_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Argumento faltante",
                description="Uso correcto: `!resenas <número>`\nEjemplo: `!resenas 3`",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Argumento inválido",
                description="El número de reseñas debe ser un número entero válido.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Sin permisos",
                description="Solo los administradores pueden usar este comando.",
                color=0xff0000
            )
            await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Resenas(bot))