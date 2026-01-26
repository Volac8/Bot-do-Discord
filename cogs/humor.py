from discord.ext import commands
import discord, random

class Humor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="desgoze")
    async def desgoze_minhas_calças(self, ctx, *, args):
        """Desgoza calças"""
        t = random.randint(1, 2)
        await ctx.send(f"AAAAAAAAAAaaaAaAaaaaAAAAAaaa - {args}")

        if t == 1:
            await ctx.send("Não foi possível desgozar suas calças devido ao excesso de líquidos")
        else:
            await ctx.send("Suas calças foram desgozadas com sucesso senhor. Aproveite suas calças limpas")

    @commands.command(name="amoleça")
    async def amoleça_meu_pinto(self, ctx, *, args):
        """Amolece pinto"""
        t = random.randint(1, 2)
        if t == 1:
            await ctx.send("Sinto muito senhor, objeto rígido demais.")
        else:
            await ctx.send("Amolecimento concluído, você pode voltar a caminhar normalmente")

    @commands.command(name="here")
    async def here_comes_the_sun(self, ctx, *, args):
        """The sun has come"""
        await ctx.send("Turururu")

    @commands.command(name="amaldiçoe")
    async def amaldiçoe(self, ctx, membro: discord.Member):
        """Amaldiçoa um membro"""
        frases = [
            "VOCÊ ACHA MESMO QUE VAI SOBREVIVER A PRÓXIMA SESSÃO? :morra:1134895781229363330 **_Sons de raio_**",
            "SEU PRÓXIMO d20 SERÁ 1! :morra:1134895781229363330 **_Sons de raio_**",
            "RESPIRAÇÃO AUTOMÁTICA DESLIGADA :morra:1134895781229363330 **_Sons de raio_**",
            "QUE SUA CAMISINHA ESTOURE :morra:1134895781229363330 **_Sons de raio**",
            "QUE SUA RINITE ATAQUE :morra:1134895781229363330 **_Sons de raio_**",
            ""
        ]

        frase_escolhida = random.choice(frases)
        await ctx.send(f"{membro.mention} – {frase_escolhida}")

    @commands.command(name="xingue")
    async def xingue(self, ctx, membro: discord.Member):
        """Xinga um membro"""
        frases = [
            "Porque você não vai tomar no seu cu?",
            "ENTÃO POR QUE VOCÊ NÃO SE MATA?",
            "VOU MOLESTAR ESSA PUTA",
            "Nossa você é um fudido vai tomar no seu cu velho -by Const",
            "Eca, Preto",
            "Porque você não coloca para alugar todo esse espaço vazio no seu cérebro?",
            "Se você pulasse da altura do seu ego para o seu QI, você sairia daqui aleijado.",
            "Coloca uma dentadura no cu e ri pro caralho fdp",
            "O mundo tem oito bilhões de pessoas e de todas essas você é a razão da legalização do aborto",
            "Torcedor do Vasca da Gama"
        ]

        frase_escolhida = random.choice(frases)
        await ctx.send(f"{membro.mention} {frase_escolhida}")

def setup(bot):
    bot.add_cog(Humor(bot))