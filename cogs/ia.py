import random
from discord.ext import commands
from utils.utils import obter_conversa
import discord, openai

class IA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="defina")
    async def defina(self, ctx, *, termo: str):
        """Define um termo usando IA"""

        prompt = (
            f"Você é um dicionário em português. "
            f"Defina de forma clara e concisa a palavra ou expressão '{termo}' "
            f"e apresente um exemplo de uso em uma frase."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "Você é um dicionário em português."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=200
            )
            conteudo = response.choices[0].message.content.strip() # type: ignore

            text = [
                "**Fonte: Vozes da minha cabeça**",
                "**Fonte: Arial**",
                "**Fonte: Comic Sans 12**",
                "**Fonte: ***Imagem de uma fonte***",
                "**Fonte: A sua mãe aquela gostosa**",
                "**Fonte: A minha pika**",
                "**Fonte: Chat GPT**",
                "**Fonte: O Macaco roxo que eu baixei sem querer**",
                "**Fonte: Google**",
                "**Fonte: Dicionario**",
                "**Fonte: Aurerio**",
            ]

            fonte_escolhida = random.choice(text)
            res = conteudo + "\n\n" + fonte_escolhida

            await ctx.send(res)

        except Exception as e:
            await ctx.send("Karalho brother você escreveu em hieróglifos filho da puta?")
            print(f"[ERRO] defina: {e}")

    @commands.command(name="defenda-me")
    async def defender(self, ctx, quantidade: int = 50):
        """Defende você em um debate"""
        canal = ctx.channel
        reu = ctx.author
        mensagens = []
        async for msg in canal.history(limit=quantidade + 10):
            if msg.author.bot:
                continue
            if msg.id == ctx.message.id:
                continue
            mensagens.append(f"{msg.author.name}: {msg.content}")

        if not mensagens:
            return await ctx.send("é foda, não tenho contexto o bastante para te defender.")

        mensagens = list(reversed(mensagens))
        conversa_texto = "\n".join(mensagens)

        prompt = (
            f"Você é um assistente que sempre defende a posição de '{reu}' "
            "em qualquer debate. Abaixo está o histórico recente de uma conversa. "
            "Baseado nisso, produza um texto argumentativo coerente e persuasivo, "
            f"defendendo o ponto de vista do {reu} frente aos argumentos apresentados.\n\n"
            f"{conversa_texto}\n\n"
            "Resposta:"
        )

        try:
            resp = openai.ChatCompletion.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "Você defende sempre o usuário."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            resposta = resp.choices[0].message.content.strip() # type: ignore
            embed = discord.Embed(
                title="Veja bem, em defesa do meu cliente...",
                description=resposta,
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            print(f"[ERRO defender] {e}")
            await ctx.send("puta que pariu, ai tbm nem eu consigo te defender")

    @commands.command(name="resumir")
    async def resumir(self, ctx, quantidade: int = 50):
        """Resume a conversa recente"""
        conversa = obter_conversa()
        if not conversa:
            await ctx.send("❌ Não há conversa suficiente para resumir.")
            return

        quantidade = min(quantidade, len(conversa))
        mensagens_para_resumir = conversa[-quantidade:]
        texto = "\n".join([f"{msg['autor']}: {msg['conteudo']}" for msg in mensagens_para_resumir])

        prompt = f"Resuma a seguinte conversa entre usuários de Discord:\n\n{texto}"

        try:
            resposta = openai.ChatCompletion.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente que resume conversas do Discord de forma clara e breve."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            resumo = resposta.choices[0].message.content # type: ignore
            await ctx.send(f"📄 **Resumo das últimas {quantidade} mensagens:**\n{resumo}")
        except Exception as e:
            print(f"[ERRO] resumir: {e}")
            await ctx.send("Erro ao resumir conversa.")

def setup(bot):
    bot.add_cog(IA(bot))