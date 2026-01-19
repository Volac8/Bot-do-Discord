from discord.ext import commands
import discord
import random

async def setup(bot):
    await bot.add_cog(ComandosPersonalizados(bot))

class ComandosPersonalizados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def piada(self, ctx):
        piadas = [
            "Por que o livro foi ao médico? Porque tinha muitas páginas doentes!",
            "O que o pato falou para a pata? Vem Quá!",
            "Por que o computador foi ao médico? Porque estava com vírus!",
            "Qual é o peixe mais inteligente? O peixe-papagaio!",
            "Por que a galinha atravessou a rua? Para chegar do outro lado!"
        ]
        await ctx.send(random.choice(piadas))

    @commands.command()
    async def ofenda(self, ctx, member: discord.Member):
        await ctx.send(f"{member.mention} sinta-se ofendido!")

    @commands.command()
    async def musgocomer(self, ctx):
        await ctx.send(":musgocomer:1386755463374438560 nham nham")


