import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import random
import time
import aiohttp
import pytz
from datetime import datetime
from cogs.legit import staff_vouchers, save_vouchs

RESET_ROLE_ID = 1368403966014001192
ALLOWED_USER_IDS = [1334240796278259893, 1385082644424949760]
ALERT_USER_IDS = [1373757431821238272, 1385082644424949760, 1334240796278259893]

class ConfirmResetView(discord.ui.View):
    def __init__(self, author_id, on_confirm, on_cancel):
        super().__init__(timeout=120)
        self.author_id = author_id
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

    @discord.ui.button(label="¡Sí!", style=discord.ButtonStyle.danger)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Solo quien ejecutó el comando puede usar esto.", ephemeral=True)
        await interaction.response.edit_message(content="🕒 Eliminando todos los vouchs...\nTiempo estimado: 3 minutos.", view=None)
        await self.on_confirm(interaction)

    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message("❌ Solo quien ejecutó el comando puede usar esto.", ephemeral=True)
        await interaction.response.edit_message(content="❌ Cancelado. No se eliminarán los vouchs.", view=None)
        await self.on_cancel(interaction)

class CancelByDMView(discord.ui.View):
    def __init__(self, author, cancelar_callback, bot, reset_context):
        super().__init__(timeout=180)
        self.author = author
        self.cancelar_callback = cancelar_callback
        self.bot = bot
        self.reset_context = reset_context

    @discord.ui.button(label="Cancelar Comando", style=discord.ButtonStyle.danger)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.cancelar_callback(interaction)

class Seguridad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_used = {}
        self.reset_context = {}
        self.dm_messages = {}

    def has_access(self, member):
        return member.id in ALLOWED_USER_IDS or any(role.id == RESET_ROLE_ID for role in member.roles)

    def get_random_captcha(self):
        pool = ["🌞", "❄️", "🧠", "🐉", "⚡", "🧩", "🕵️", "🦴", "💣", "🛸"]
        return random.choice(pool)

    async def get_geo_info(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://ip-api.com/json") as r:
                data = await r.json()
                return {
                    "country": data.get("country", "Desconocido"),
                    "city": data.get("city", "Desconocido"),
                    "timezone": data.get("timezone", "UTC")
                }

    async def enviar_alerta_dm(self, author, tiempo_estimado, cancelar_callback):
        for uid in ALERT_USER_IDS:
            user = self.bot.get_user(uid)
            if user:
                embed = discord.Embed(
                    title="🚨 Comando ResetVouch Activado",
                    description=(
                        f"<a:Alerta:1359951911830290666> {author.mention} ha usado el comando `Resetvouch`\n\n"
                        f"Tienes **{tiempo_estimado}** para **cancelar** esta opción.\n"
                        f"Si lo dejas pasar, se eliminarán todos los vouchs. <a:Alerta:1359951911830290666>"
                    ),
                    color=discord.Color.red()
                )
                view = CancelByDMView(author, self.cancelar_comando, self.bot, self.reset_context)
                try:
                    message = await user.send(embed=embed, view=view)
                    self.dm_messages[uid] = message
                except:
                    pass

    async def ejecutar_reseteo(self, interaction):
        self.reset_context[interaction.user.id] = interaction.channel
        await self.enviar_alerta_dm(interaction.user, "3 minutos", self.cancelar_comando)
        await asyncio.sleep(180)
        if interaction.user.id not in self.reset_context:
            return

        geo = await self.get_geo_info()
        tz = pytz.timezone(geo["timezone"])
        hora_local = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        for uid in ALERT_USER_IDS:
            user = self.bot.get_user(uid)
            if user:
                embed = discord.Embed(
                    title="🧨 Todos los vouchs fueron eliminados",
                    description=(
                        f"<a:Alerta:1359951911830290666> {interaction.user.mention} ha reseteado todos los vouchs.\n\n"
                    ),
                    color=discord.Color.red()
                )
                try:
                    await user.send(embed=embed)
                except:
                    pass

        staff_vouchers.clear()
        save_vouchs()
        await interaction.channel.send("✅ Todos los vouchs han sido eliminados correctamente.")
        del self.reset_context[interaction.user.id]
        self.dm_messages.clear()

    async def cancelar_comando(self, interaction):
        canceler = interaction.user

        for uid, canal in self.reset_context.items():
            await canal.send(f"🛑 El admin {canceler.mention} ha cancelado el Reset de Vouchs.")
            for alert_id in ALERT_USER_IDS:
                if alert_id != canceler.id:
                    user = self.bot.get_user(alert_id)
                    if user:
                        try:
                            await user.send(f"🛑 El admin {canceler.mention} ha cancelado el comando `Resetvouch`.")
                        except:
                            pass
            break

        for uid, msg in self.dm_messages.items():
            if uid != canceler.id:
                try:
                    await msg.edit(content="❌ El comando fue cancelado por otro administrador.", view=None)
                except:
                    pass

        self.dm_messages.clear()
        self.reset_context.clear()
        await interaction.response.send_message("❌ Comando cancelado exitosamente.", ephemeral=True)

    async def iniciar_reset(self, ctx_or_interaction, sin_cooldown=False):
        user_id = ctx_or_interaction.user.id if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author.id
        now = time.time()
        if not sin_cooldown:
            if user_id in self.last_used and now - self.last_used[user_id] < 7200:
                return await self.enviar(ctx_or_interaction, "❌ Este comando solo puede usarse cada 2 horas.")
            self.last_used[user_id] = now

        captcha = self.get_random_captcha()

        def check(m):
            return m.author.id == user_id and m.content.strip() == captcha

        await self.enviar(ctx_or_interaction, f"🔐 Captcha: Escribe el siguiente símbolo exactamente como lo ves: `{captcha}`")

        try:
            await self.bot.wait_for("message", timeout=30.0, check=check)
            view = ConfirmResetView(user_id, self.ejecutar_reseteo, self.cancelar_comando)
            await self.enviar(ctx_or_interaction, "**⚠️ Advertencia:** Esta acción eliminará **todos los vouchs registrados**. ¿Estás seguro?", view=view)
        except asyncio.TimeoutError:
            await self.enviar(ctx_or_interaction, "⏱️ Tiempo agotado. Captcha no resuelto.")

    async def enviar(self, where, content, view=None):
        if isinstance(where, discord.Interaction):
            await where.response.send_message(content, ephemeral=False, view=view)
        else:
            await where.send(content, view=view)

    @commands.command(name="resetvouchs")
    async def resetvouchs_prefix(self, ctx):
        if not self.has_access(ctx.author):
            return await ctx.send("❌ No tienes permisos.")
        await self.iniciar_reset(ctx)

    @app_commands.command(name="resetvouchs", description="Resetea todos los vouchs (solo admins autorizados)")
    async def resetvouchs_slash(self, interaction: discord.Interaction):
        if not self.has_access(interaction.user):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        await self.iniciar_reset(interaction)

    @commands.command(name="s")
    async def s_secreto_reset(self, ctx):
        if not self.has_access(ctx.author):
            return await ctx.send("❌ No tienes permisos.")
        await self.iniciar_reset(ctx, sin_cooldown=True)

async def setup(bot):
    await bot.add_cog(Seguridad(bot))