from discord.ext import commands
from utils.utils import carregar_duelos, registrar_vitoria
import discord, openai, asyncio

class Duelo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="eu")
    async def eu_exijo_um_duelo(self, ctx, *, args):
        """Inicia um duelo entre dois participantes"""
        await self.iniciar_duelo(ctx)

    async def iniciar_duelo(self, message):
        await message.channel.send("⚔️ Quem são os dois participantes do duelo? Mencione ambos com @.")

        def check_mention(m):
            return m.channel == message.channel and len(m.mentions) == 2 and m.author == message.author

        try:
            participantes_msg = await self.bot.wait_for("message", timeout=60, check=check_mention)
            duelistas = participantes_msg.mentions

            await message.channel.send("Qual será a modalidade do duelo? (moggada, ofensa, criatividade)")
            def check_modalidade(m):
                return m.channel == message.channel and m.author == message.author
            modalidade_msg = await self.bot.wait_for("message", timeout=30, check=check_modalidade)
            modalidade = modalidade_msg.content.strip().lower()

            if modalidade not in ["moggada", "ofensa", "criatividade"]:
                await message.channel.send("Modalidade inválida. Duelo cancelado.")
                return

            await message.channel.send(f"{duelistas[0].mention}, envie sua {modalidade}!")
            resposta1 = await self.bot.wait_for("message", timeout=60, check=lambda m: m.author == duelistas[0])

            await message.channel.send(f"{duelistas[1].mention}, agora é sua vez!")
            resposta2 = await self.bot.wait_for("message", timeout=60, check=lambda m: m.author == duelistas[1])

            await message.channel.send("🧠 Deixe eu consultar as vozes da minha cabeça...")

            await self.avaliar_duelo(message.channel, duelistas, resposta1.content, resposta2.content, modalidade)

        except asyncio.TimeoutError:
            await message.channel.send("Tempo esgotado. Duelo cancelado.")

    async def avaliar_duelo(self, channel, duelistas, fala1, fala2, modalidade):
        await channel.send(f"⏳ Analisando as respostas para o duelo de **{modalidade}**...")

        user1, user2 = duelistas

        prompt = (
            f"Dois usuários estão participando de um duelo de **{modalidade}**.\n"
            f"Avalie qual deles mandou melhor com base em criatividade, impacto e humor.\n"
            f"Escolha **apenas um vencedor** de forma clara.\n\n"
            f"{user1.name}: \"{fala1}\"\n"
            f"{user2.name}: \"{fala2}\"\n\n"
            f"Quem venceu? Justifique brevemente sua decisão."
        )

        try:
            resposta = openai.ChatCompletion.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "Você é um árbitro experiente em duelos criativos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            resultado = resposta.choices[0].message.content.strip() # type: ignore
            await channel.send(f"🤖 **Resultado do duelo:**\n{resultado}")

            if user1.name.lower() in resultado.lower():
                vencedor = user1
            elif user2.name.lower() in resultado.lower():
                vencedor = user2
            else:
                await channel.send("Empate detectado ou resultado inconclusivo. Ninguém ganhou uma medalha.")
                return

            registrar_vitoria(vencedor.id, vencedor.name)
            await channel.send(f"🏅 {vencedor.mention} ganhou uma **medalha de honra** e subiu no ranking de duelistas!")

        except Exception as e:
            await channel.send("⚠️ Ocorreu um erro ao tentar avaliar o duelo. Tente novamente mais tarde.")
            print(f"[ERRO] avaliar_duelo: {e}")

    @commands.command(name="rankduelos")
    async def rank_duelos(self, ctx):
        """Mostra o ranking dos duelistas"""
        dados = carregar_duelos()
        if not dados:
            await ctx.send("Ainda não há registros de duelos.")
            return

        ranking = sorted(dados.items(), key=lambda item: item[1]["vitorias"], reverse=True)

        embed = discord.Embed(title="🏆 Ranking de Duelistas", color=discord.Color.gold())

        for i, (user_id, info) in enumerate(ranking, start=1):
            medalha = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🎖️"
            embed.add_field(
                name=f"{medalha} {info['nome']}",
                value=f"Vitórias: {info['vitorias']}",
                inline=False
            )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Duelo(bot))