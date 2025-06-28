import discord
from discord.ext import commands
from discord import app_commands

class CustomHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="📜 Mi Lista de Comandos",
            description="Te la dejo por aquí abajo",
            color=discord.Color.red()
        )
        embed.add_field(
            name="<a:DINERO2:1359259348706267218> | vx2 / vx3",
            value="Activa el evento vouchs x2/x3\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<:supremeno:1369724681854390424> | vcancelar",
            value="Cancela un evento activo\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<a:Rules:1359951505083465738> | topG",
            value="Visualisa los tops vouchers",
            inline=False
        )
        embed.add_field(
            name="<a:SelfRoles:1380502163322699886> | addvouchs",
            value="Añade vouchers a algún usuario\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<:bot_owner:1357094480028893325> | delvouchs",
            value="Elimina Vouchs a algún usuario\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<a:wasaa:1293663454640734248> | vouchs",
            value="Revisa tus vouchs o los de alguien más",
            inline=False
        )
        embed.add_field(
            name="<a:Isaac:1371985526424604732> | resetvouchs",
            value="Resetea todos los vouchs registrados\n*_(solo rol autorizado)_*",
            inline=False
        )
        embed.set_footer(text="` SupremeCm voucher system`")
        await ctx.send(embed=embed)

    @app_commands.command(name="help", description="Muestra todos los comandos disponibles del bot.")
    async def slash_help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Mi Lista de Comandos",
            description="Te la dejo por aquí abajo",
            color=discord.Color.red()
        )
        embed.add_field(
            name="<a:DINERO2:1359259348706267218> | vx2 / vx3",
            value="Activa el evento vouchs x2/x3\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<:supremeno:1369724681854390424> | vcancelar",
            value="Cancela un evento activo\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<a:Rules:1359951505083465738> | topG",
            value="Visualisa los tops vouchers",
            inline=False
        )
        embed.add_field(
            name="<a:SelfRoles:1380502163322699886> | addvouchs",
            value="Añade vouchers a algún usuario\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<:bot_owner:1357094480028893325> | delvouchs",
            value="Elimina Vouchs a algún usuario\n*_(solo admins autorizados)_*",
            inline=False
        )
        embed.add_field(
            name="<a:wasaa:1293663454640734248> | vouchs",
            value="Revisa tus vouchs o los de alguien más",
            inline=False
        )
        embed.add_field(
            name="<a:Isaac:1371985526424604732> | resetvouchs",
            value="Resetea todos los vouchs registrados\n*_(solo rol autorizado)_*",
            inline=False
        )
        embed.set_footer(text="` SupremeCm voucher system`")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomHelp(bot))