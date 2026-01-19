from discord.ext import commands
import discord, random, asyncio, openai
from datetime import datetime, timedelta
from utils import (
    carregar_agenda, salvar_agenda, carregar_duelos, salvar_duelos, 
    registrar_vitoria, adicionar_mensagem, obter_conversa, 
    agendar_notificacoes, get_scheduler
)

async def setup(bot):
    await bot.add_cog(ComandosPersonalizados(bot))

class ComandosPersonalizados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.agenda_rpg = carregar_agenda()

    # ===== COMANDOS ORIGINAIS =====

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

    # ===== COMANDOS DE DUELO =====

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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um árbitro experiente em duelos criativos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            resultado = resposta.choices[0].message.content.strip()
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

    # ===== COMANDOS DE HUMOR =====

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
        await ctx.send(f"{membro.mention} – {frase_escolhida}")

    # ===== COMANDOS DE IA =====

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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um dicionário em português."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=200
            )
            conteudo = response.choices[0].message.content.strip()

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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você defende sempre o usuário."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=200
            )
            resposta = resp.choices[0].message.content.strip()
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
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente que resume conversas do Discord de forma clara e breve."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )

            resumo = resposta.choices[0].message.content
            await ctx.send(f"📄 **Resumo das últimas {quantidade} mensagens:**\n{resumo}")
        except Exception as e:
            print(f"[ERRO] resumir: {e}")
            await ctx.send("Erro ao resumir conversa.")

    # ===== COMANDOS DE AGENDA =====

    @commands.command(name="agendar")
    async def agendar(self, ctx):
        """Agenda um RPG"""
        await ctx.send("📅 Envie a data e hora do RPG no formato `DD/MM/AAAA HH:MM`:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg_data = await self.bot.wait_for("message", timeout=60, check=check)
            data_str = msg_data.content.strip()
            new_start = datetime.strptime(data_str, "%d/%m/%Y %H:%M")

            for key, item in self.agenda_rpg.items():
                old_start = datetime.strptime(key, "%d/%m/%Y %H:%M")
                old_end = old_start + timedelta(minutes=item["duracao_min"])
                if new_start < old_end and new_start > old_start:
                    await ctx.send(
                        f"⚠️ Conflito de horário! Este RPG se sobrepõe ao agendado em `{key}`: **{item['descricao']}**"
                    )
                    return

            await ctx.send("⏱️ Qual a duração da sessão? Formato `HH:MM`")
            msg_dur = await self.bot.wait_for("message", timeout=30, check=check)
            h, m = map(int, msg_dur.content.strip().split(":"))
            new_dur_min = h * 60 + m

            chave = new_start.strftime("%d/%m/%Y %H:%M")
            await ctx.send("📝 Qual é a descrição da sessão?")
            msg_desc = await self.bot.wait_for("message", timeout=30, check=check)
            descricao = msg_desc.content.strip()

            await ctx.send("📛 Marque o cargo do RPG (ex: @Aventureiros).")
            msg_cargo = await self.bot.wait_for("message", timeout=30, check=check)

            if not msg_cargo.role_mentions:
                return await ctx.send("❌ Você precisa mencionar um cargo válido com `@nome_do_cargo`.")

            cargo = msg_cargo.role_mentions[0]

            self.agenda_rpg[chave] = {
                "autor": ctx.author.name,
                "descricao": descricao,
                "cargo_id": cargo.id,
                "canal_id": ctx.channel.id,
                "duracao_min": new_dur_min
            }
            salvar_agenda()
            agendar_notificacoes(self.bot, new_start, ctx.channel.id, cargo.id, descricao, new_dur_min)

            await ctx.send(
                f"✅ RPG agendado para {chave}, duração {h:02d}:{m:02d}, com cargo {cargo.mention}!"
            )

        except Exception as e:
            await ctx.send("⏰ Tempo esgotado ou erro de formato. Tente novamente.")
            print(f"[ERRO] agendar: {e}")

    @commands.command(name="listar")
    async def listar(self, ctx):
        """Lista os RPGs agendados"""
        self.agenda_rpg = carregar_agenda()
        if not self.agenda_rpg:
            return await ctx.send("📭 Nenhum RPG agendado.")

        linhas = []
        for i, data_str in enumerate(sorted(self.agenda_rpg), start=1):
            item = self.agenda_rpg[data_str]
            linhas.append(f"{i}. `{data_str}` – {item['descricao']}")

        texto = "📋 **Agenda de RPGs (use o número para excluir):**\n" + "\n".join(linhas)
        await ctx.send(texto)

    @commands.command(name="excluir")
    async def excluir(self, ctx, arg: str = None):
        """Exclui um RPG da agenda"""
        self.agenda_rpg = carregar_agenda()
        if not self.agenda_rpg:
            return await ctx.send("📭 Nenhum RPG para excluir.")

        keys = sorted(self.agenda_rpg)

        if arg and arg.isdigit():
            idx = int(arg) - 1
            if 0 <= idx < len(keys):
                chave = keys[idx]
            else:
                return await ctx.send("❌ Índice inválido.")
        elif arg:
            chave = arg.strip()
            if chave not in self.agenda_rpg:
                return await ctx.send("❌ Não encontrei nenhum RPG nessa data/hora.")
        else:
            await ctx.send("🗑️ Digite o número ou a data/hora (DD/MM/AAAA HH:MM) do RPG a excluir:")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for("message", timeout=30, check=check)
                content = msg.content.strip()
                if content.isdigit():
                    idx = int(content) - 1
                    if 0 <= idx < len(keys):
                        chave = keys[idx]
                    else:
                        return await ctx.send("❌ Índice inválido.")
                else:
                    chave = content
                    if chave not in self.agenda_rpg:
                        return await ctx.send("❌ Não encontrei nenhum RPG nessa data/hora.")
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Tempo esgotado. Tente de novo.")

        info = self.agenda_rpg.pop(chave)
        salvar_agenda()
        await ctx.send(f"✅ RPG de `{chave}` ({info['descricao']}) excluído.")

    @commands.command(name="agendados")
    async def agendados(self, ctx):
        """Mostra todos os RPGs agendados"""
        self.agenda_rpg = carregar_agenda()
        if not self.agenda_rpg:
            await ctx.send("Tragicamente não há nenhum rpg agendado")
            return

        resposta = "📅 **Agenda de RPGs:**\n"
        for data_str in sorted(self.agenda_rpg):
            item = self.agenda_rpg[data_str]
            resposta += f"🕒 `{data_str}` - {item['descricao']} \n"
        await ctx.send(resposta)

    @commands.command(name="anote")
    async def anote(self, ctx):
        """Cria um lembrete"""
        await ctx.send("📝 O que você quer que eu te lembre?")
        def check(m): return m.author == ctx.author and m.channel == ctx.channel
        try:
            msg_lembrar = await self.bot.wait_for("message", timeout=60, check=check)
            conteudo = msg_lembrar.content.strip()

            await ctx.send("⏰ Quando? (formato `DD/MM/AAAA HH:MM` ou `diario HH:MM` ou `semanal DIA HH:MM`)\nExemplos:\n`05/08/2025 19:30`\n`diario 08:00`\n`semanal segunda 18:00`")
            msg_quando = await self.bot.wait_for("message", timeout=60, check=check)
            info = msg_quando.content.lower().strip()

            canal_id = ctx.channel.id
            autor_id = ctx.author.id
            scheduler = get_scheduler()

            if info.startswith("diario "):
                hora = datetime.strptime(info.split(" ")[1], "%H:%M").time()
                scheduler.add_job(
                    lambda: self.bot.loop.create_task(
                        self.bot.get_channel(canal_id).send(f"⏰ <@{autor_id}> lembrete diário: {conteudo}")
                    ),
                    trigger="cron", hour=hora.hour, minute=hora.minute
                )
                await ctx.send("✅ Ta feito chefia")

            elif info.startswith("semanal "):
                partes = info.split(" ")
                dia_semana = partes[1]
                hora = datetime.strptime(partes[2], "%H:%M").time()
                dias = {
                    "segunda": "mon", "terça": "tue", "quarta": "wed",
                    "quinta": "thu", "sexta": "fri", "sábado": "sat", "domingo": "sun"
                }
                if dia_semana not in dias:
                    return await ctx.send(" é pra escrever dia de semana o imbecil.")
                scheduler.add_job(
                    lambda: self.bot.loop.create_task(
                        self.bot.get_channel(canal_id).send(f"📆 <@{autor_id}> lembrete semanal ({dia_semana}): {conteudo}")
                    ),
                    trigger="cron", day_of_week=dias[dia_semana], hour=hora.hour, minute=hora.minute
                )
                await ctx.send("✅ Ta feito chefia")

            else:
                data = datetime.strptime(info, "%d/%m/%Y %H:%M")
                scheduler.add_job(
                    lambda: self.bot.loop.create_task(
                        self.bot.get_channel(canal_id).send(f"🔔 <@{autor_id}> lembrete: {conteudo}")
                    ),
                    trigger="date", run_date=data
                )
                await ctx.send("✅ Ta feito chefia ")

        except Exception as e:
            await ctx.send("❌ Erro ao configurar lembrete. Verifique o formato e tente novamente.")
            print(f"[ERRO] anote: {e}")






    @commands.command(name="fazueli")
    async def fazueli(self, ctx):
            await ctx.send("L")