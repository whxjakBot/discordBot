import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from discord.ui import View, Button
from discord import Interaction
import json
import os

ALLOWED_CHANNELS = [1381407391492472984, 1381407389999169638]
ALLOWED_ROLE_ID = 1358905372190179660
ADMIN_VOUCH_ROLE = 1366160834874572810
ALLOWED_USER_ID = 1334240796278259893
MENTION_ROLE_ID = 1356705821492252714

staff_vouchers = {}
multiplier = 1
cancel_task = None

class Legit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin_or_vx_role(self, member):
        return (
            isinstance(member, discord.Member)
            and (member.guild_permissions.administrator or any(role.id == ADMIN_VOUCH_ROLE for role in member.roles))
        )

    def has_permission(self, ctx_or_interaction):
        member = ctx_or_interaction.user if isinstance(ctx_or_interaction, discord.Interaction) else ctx_or_interaction.author
        return (
            member.id == ALLOWED_USER_ID
            or any(role.id == ALLOWED_ROLE_ID for role in getattr(member, "roles", []))
            or self.is_admin_or_vx_role(member)
        )

    def parse_duration(self, time_str):
        try:
            if time_str.endswith("m"):
                return int(time_str[:-1]) * 60
            elif time_str.endswith("h"):
                return int(time_str[:-1]) * 3600
            else:
                return int(time_str)
        except:
            return None

    async def start_multiplier_event(self, channel, factor, duration_seconds):
        global multiplier, cancel_task
        multiplier = factor

        await channel.send(
            f"<@&{MENTION_ROLE_ID}>\nEvento de vouchs X{factor} activado durante {duration_seconds // 60} minutos"
        )

        async def end_event():
            global multiplier, cancel_task
            await asyncio.sleep(duration_seconds)
            multiplier = 1
            cancel_task = None
            await channel.send(
                f"<@&{MENTION_ROLE_ID}>\nSe ha acabado el evento (x{factor}) de vouchs\nAhora los vouchs volverán a la normalidad"
            )

        cancel_task = self.bot.loop.create_task(end_event())

    @commands.command(name="vx2")
    async def vx2_prefix(self, ctx, time: str):
        if not self.is_admin_or_vx_role(ctx.author):
            return await ctx.send("❌ No tienes permisos.")
        await ctx.message.delete()
        seconds = self.parse_duration(time)
        if seconds:
            await self.start_multiplier_event(ctx.channel, 2, seconds)

    @commands.command(name="vx3")
    async def vx3_prefix(self, ctx, time: str):
        if not self.is_admin_or_vx_role(ctx.author):
            return await ctx.send("❌ No tienes permisos.")
        await ctx.message.delete()
        seconds = self.parse_duration(time)
        if seconds:
            await self.start_multiplier_event(ctx.channel, 3, seconds)

    @commands.command(name="vcancelar")
    async def vcancelar_prefix(self, ctx):
        global multiplier, cancel_task
        if not self.is_admin_or_vx_role(ctx.author):
            return await ctx.send("❌ No tienes permisos.")
        await ctx.message.delete()
        if cancel_task:
            cancel_task.cancel()
            cancel_task = None
            multiplier = 1
            await ctx.channel.send(
                f"<@&{MENTION_ROLE_ID}>\nSe ha cancelado el evento de vouchs\nAhora los vouchs volverán a la normalidad"
            )
        else:
            await ctx.channel.send("En este momento no hay eventos activos")

    @app_commands.command(name="vx2", description="Activa evento de vouchs x2")
    async def vx2_slash(self, interaction: discord.Interaction, time: str):
        if not self.is_admin_or_vx_role(interaction.user):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        seconds = self.parse_duration(time)
        if seconds:
            await self.start_multiplier_event(interaction.channel, 2, seconds)

    @app_commands.command(name="vx3", description="Activa evento de vouchs x3")
    async def vx3_slash(self, interaction: discord.Interaction, time: str):
        if not self.is_admin_or_vx_role(interaction.user):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        seconds = self.parse_duration(time)
        if seconds:
            await self.start_multiplier_event(interaction.channel, 3, seconds)

    @app_commands.command(name="vcancelar", description="Cancela el evento de vouchs")
    async def vcancelar_slash(self, interaction: discord.Interaction):
        global multiplier, cancel_task
        if not self.is_admin_or_vx_role(interaction.user):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        if cancel_task:
            cancel_task.cancel()
            cancel_task = None
            multiplier = 1
            await interaction.response.send_message(
                f"<@&{MENTION_ROLE_ID}>\nSe ha cancelado el evento de vouchs\nAhora los vouchs volverán a la normalidad"
            )
        else:
            await interaction.response.send_message("En este momento no hay eventos activos", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if not message.content.lower().startswith("legit"):
            return

        if message.channel.id not in ALLOWED_CHANNELS:
            return await message.channel.send(
                f"🚫 Este comando solo está permitido en <#{ALLOWED_CHANNELS[0]}> y <#{ALLOWED_CHANNELS[1]}>."
            )

        if not message.mentions:
            return await message.channel.send("❌ Debes mencionar a alguien para darle el voucher.")

        try:
            await message.delete()

            autor = message.author.mention
            staff_user = message.mentions[0]
            staff = staff_user.mention
            staff_id = staff_user.id

            parts = message.content.split()
            servicio = " ".join(parts[2:]).strip() if len(parts) >= 3 else "Servicio no especificado"

            staff_vouchers[staff_id] = staff_vouchers.get(staff_id, 0) + multiplier
            save_vouchs()
            total = staff_vouchers[staff_id]

            embed = discord.Embed(
                description=(
                    f"Gracias {autor} por el vouch\n"
                    f"<a:starsssa:1360796055868014863> {staff} tiene {total} Vouchs "
                    f"por el ítem: {servicio} <a:signo_white:1358183397868044458>"
                ),
                color=discord.Color.dark_blue()
            )

            await message.channel.send(embed=embed)

        except Exception as e:
            print(f"❌ Error en legit: {e}")

    @commands.command(name="addvouchs")
    async def addvouchs_prefix(self, ctx, member: discord.Member, amount: int):
        if not self.has_permission(ctx):
            return await ctx.send("❌ No tienes permisos.")
        await self._handle_add(ctx, member, amount)

    @commands.command(name="delvouchs")
    async def delvouchs_prefix(self, ctx, member: discord.Member, amount: int):
        if not self.has_permission(ctx):
            return await ctx.send("❌ No tienes permisos.")
        await self._handle_del(ctx, member, amount)

    @app_commands.command(name="addvouchs", description="Agrega vouchs a un miembro.")
    async def addvouchs_slash(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not self.has_permission(interaction):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        await self._handle_add(interaction, member, amount)

    @app_commands.command(name="delvouchs", description="Quita vouchs a un miembro.")
    async def delvouchs_slash(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not self.has_permission(interaction):
            return await interaction.response.send_message("❌ No tienes permisos.", ephemeral=True)
        await self._handle_del(interaction, member, amount)

    async def _handle_add(self, where, member, amount):
        staff_vouchers[member.id] = staff_vouchers.get(member.id, 0) + amount
        save_vouchs()
        total = staff_vouchers[member.id]

        embed = discord.Embed(
            title="📈 Vouchs Actualizados",
            description=(
                f"<a:Skeleto:1357114206432002108> Se han agregado {amount} vouchs a {member.mention}.\n\n"
                f"📊 Ahora tiene {total} vouchs."
            ),
            color=discord.Color.green()
        )

        if isinstance(where, discord.Interaction):
            await where.response.send_message(embed=embed)
        else:
            await where.send(embed=embed)

    async def _handle_del(self, where, member, amount):
        staff_vouchers[member.id] = max(0, staff_vouchers.get(member.id, 0) - amount)
        save_vouchs()
        total = staff_vouchers[member.id]

        embed = discord.Embed(
            title="📉 Vouchs Actualizados",
            description=(
                f"<a:Skeleto:1357114206432002108> Se le han quitado {amount} vouchs a {member.mention}.\n\n"
                f"📊 Ahora tiene {total} vouchs."
            ),
            color=discord.Color.red()
        )

        if isinstance(where, discord.Interaction):
            await where.response.send_message(embed=embed)
        else:
            await where.send(embed=embed)

    @commands.command(name="topG")
    async def topg_prefix(self, ctx):
        await self.show_top_vouchers(ctx)

    @app_commands.command(name="topvouchs", description="Tops Vouch")
    async def topvouchs_slash(self, interaction: discord.Interaction):
        await self.show_top_vouchers(interaction)

    async def show_top_vouchers(self, where):
        entries = sorted(staff_vouchers.items(), key=lambda x: x[1], reverse=True)
        pages = [entries[i:i + 5] for i in range(0, len(entries), 5)]
        if not pages:
            return await self.send_response(where, "❌ No hay vouchs registrados aún.")
        await self.send_top_page(where, pages, 0)

    async def send_top_page(self, where, pages, page_index):
        page = pages[page_index]
        embed = discord.Embed(
            title="<a:bailando:1359951489153499369> Top Vouchers <a:bailando:1359951489153499369>",
            color=0xa70000
        )

        start_rank = page_index * 5 + 1
        lines = []
        for i, (user_id, vouchs) in enumerate(page, start=start_rank):
            user = self.bot.get_user(user_id)
            username = user.name if user else f"Usuario {user_id}"
            lines.append(f"~Top {i} {username} {vouchs} vouchs")
        embed.description = "\n".join(lines)
        embed.set_footer(text=f"Página {page_index + 1} de {len(pages)}")

        view = TopPaginationView(pages, page_index, self.send_top_page, where)
        await self.send_response(where, embed=embed, view=view)

    async def send_response(self, where, content=None, embed=None, view=None):
        if isinstance(where, discord.Interaction):
            if where.response.is_done():
                await where.followup.send(content=content, embed=embed, view=view, ephemeral=False)
            else:
                await where.response.send_message(content=content, embed=embed, view=view, ephemeral=False)
        else:
            await where.send(content=content, embed=embed, view=view)

    @commands.command(name="vouchs")
    async def vouchs_prefix(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        vouchs = staff_vouchers.get(member.id, 0)

        embed = discord.Embed(
            description=f"<a:Rules:1359951505083465738>  El Usuario {member.mention} Tiene actualmente {vouchs} <a:Rules:1359951505083465738>",
            color=discord.Color.blurple()
        )

        await ctx.send(embed=embed)

    @app_commands.command(name="vouchs", description="Mira los Vouchs de alguien")
    @app_commands.describe(user="Usuario a consultar (opcional)")
    async def vouchs_slash(self, interaction: discord.Interaction, user: discord.User = None):
        user = user or interaction.user
        vouchs = staff_vouchers.get(user.id, 0)

        embed = discord.Embed(
            description=f"<a:Rules:1359951505083465738>  El Usuario {user.mention} Tiene actualmente {vouchs} Vouchs<a:Rules:1359951505083465738>",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=False)

class TopPaginationView(View):
    def __init__(self, pages, current_page, callback, where):
        super().__init__(timeout=60)
        self.pages = pages
        self.current_page = current_page
        self.callback = callback
        self.where = where

        self.prev_button = Button(emoji="<:dotsupreme:1369732120108466196>", style=discord.ButtonStyle.gray)
        self.next_button = Button(emoji="<:dotsupremewhite:1369732223640539267>", style=discord.ButtonStyle.gray)

        self.prev_button.callback = self.prev_page
        self.next_button.callback = self.next_page

        if self.current_page > 0:
            self.add_item(self.prev_button)
        if self.current_page < len(pages) - 1:
            self.add_item(self.next_button)

    async def prev_page(self, interaction: Interaction):
        self.current_page -= 1
        await self.callback(interaction, self.pages, self.current_page)

    async def next_page(self, interaction: Interaction):
        self.current_page += 1
        await self.callback(interaction, self.pages, self.current_page)

# JSON LOAD & SAVE FUNCIONES

VOUCHS_FILE = "vouchs_data.json"

def load_vouchs():
    global staff_vouchers
    if os.path.exists(VOUCHS_FILE):
        with open(VOUCHS_FILE, "r") as f:
            data = json.load(f)
            staff_vouchers = {int(k): int(v) for k, v in data.items()}
    staff_vouchers.pop(1219795515252670484, None)
    save_vouchs()

def save_vouchs():
    with open(VOUCHS_FILE, "w") as f:
        json.dump(staff_vouchers, f)

async def setup(bot):
    load_vouchs()
    await bot.add_cog(Legit(bot))