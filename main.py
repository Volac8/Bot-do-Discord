import discord, json, os, asyncio, random, openai
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

class Jarvis(commands.Bot):
    async def setup_hook(self):
        await self.load_extension("comandos_personalizados")
        await self.load_extension("evolucao")
bot = Jarvis(command_prefix="Jarvis, ", intents=intents)

scheduler = AsyncIOScheduler()

ARQUIVO = "Bot do Discord/agenda_rpg.json"

CARGO_PERMITIDO_ID = [1402824050199232566, 1398015167249387560, 561686139581497375, 337276446911496192, 622645792221691905, 327258575858565120]

def usuario_tem_permissao(ctx):
    return any(c.id in CARGO_PERMITIDO_ID for c in ctx.author.roles)


if os.path.exists(ARQUIVO):
    with open(ARQUIVO, "r") as f:
        agenda_rpg = json.load(f)
else:
    agenda_rpg = {}

def salvar_agenda():
    with open(ARQUIVO, "w") as f:
        json.dump(agenda_rpg, f, indent=2)

@bot.event
async def on_ready():
    await bot.reload_extension("comandos_personalizados")
    scheduler.start()
    print(f"🤖 Bot online como {bot.user}")

    # Reagendar eventos ao reiniciar
    for chave, item in agenda_rpg.items():
        dt = datetime.strptime(chave, "%d/%m/%Y %H:%M")
        if dt > datetime.now():
            agendar_notificacoes(dt, item["canal_id"], item["cargo_id"], item["descricao"], item["duracao_min"])

conversa = []

lembretes = []

ARQUIVO_DUELOS = "duelos.json"

def carregar_duelos():
    if not os.path.exists(ARQUIVO_DUELOS):
        with open(ARQUIVO_DUELOS, "w") as f:
            json.dump({}, f)
    with open(ARQUIVO_DUELOS, "r") as f:
        return json.load(f)

def salvar_duelos(data):
    with open(ARQUIVO_DUELOS, "w") as f:
        json.dump(data, f, indent=4)

def registrar_vitoria(vencedor_id, vencedor_nome):
    dados = carregar_duelos()
    if str(vencedor_id) in dados:
        dados[str(vencedor_id)]["vitorias"] += 1
    else:
        dados[str(vencedor_id)] = {
            "nome": vencedor_nome,
            "vitorias": 1
        }
    salvar_duelos(dados)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    conversa.append({
        "autor": message.author.name,
        "conteudo": message.content,
        "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })

    if len(conversa) > 500:
        conversa.pop(0)

    await bot.process_commands(message)  # Necessário para não bloquear outros comandos


@bot.command(name="eu")
async def eu_exijo_um_duelo(ctx, *, args):
    await iniciar_duelo(ctx)

async def iniciar_duelo(message):
    await message.channel.send("⚔️ Quem são os dois participantes do duelo? Mencione ambos com @.")

    def check_mention(m):
        return m.channel == message.channel and len(m.mentions) == 2 and m.author == message.author

    try:
        participantes_msg = await bot.wait_for("message", timeout=60, check=check_mention)
        duelistas = participantes_msg.mentions

        await message.channel.send("Qual será a modalidade do duelo? (moggada, ofensa, criatividade)")
        def check_modalidade(m):
            return m.channel == message.channel and m.author == message.author
        modalidade_msg = await bot.wait_for("message", timeout=30, check=check_modalidade)
        modalidade = modalidade_msg.content.strip().lower()

        if modalidade not in ["moggada", "ofensa", "criatividade"]:
            await message.channel.send("Modalidade inválida. Duelo cancelado.")
            return

        await message.channel.send(f"{duelistas[0].mention}, envie sua {modalidade}!")
        resposta1 = await bot.wait_for("message", timeout=60, check=lambda m: m.author == duelistas[0])

        await message.channel.send(f"{duelistas[1].mention}, agora é sua vez!")
        resposta2 = await bot.wait_for("message", timeout=60, check=lambda m: m.author == duelistas[1])

        await message.channel.send("🧠 Deixe eu consultar as vozes da minha cabeça...")

        await avaliar_duelo(message.channel, duelistas, resposta1.content, resposta2.content, modalidade)

    except asyncio.TimeoutError:
        await message.channel.send("Tempo esgotado. Duelo cancelado.")


async def avaliar_duelo(channel, duelistas, fala1, fala2, modalidade):
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
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "Você é um árbitro experiente em duelos criativos."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )

        resultado = resposta.choices[0].message.content.strip()
        await channel.send(f"🤖 **Resultado do duelo:**\n{resultado}")

        # Detectar o vencedor com base na resposta
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

@bot.command(name="desgoze")
async def desgoze_minhas_calças(ctx, *, args):
    t = random.randint(1, 2)
    await ctx.send(f"AAAAAAAAAAaaaAaAaaaaAAAAAaaa - {args}")

    if t == 1:
        await ctx.send("Não foi possível desgozar suas calças devido ao excesso de líquidos")
    else:
        await ctx.send("Suas calças foram desgozadas com sucesso senhor. Aproveite suas calças limpas")

@bot.command(name="amoleça")
async def amoleça_meu_pinto(ctx, *, args):
    t = random.randint(1, 2)
    if t == 1:
        await ctx.send("Sinto muito senhor, objeto rígido demais.")
    else:
        await ctx.send("Amolecimento concluído, você pode voltar a caminhar normalmente")

@bot.command(name="here")
async def here_comes_the_sun(cyx, *, args):
    await ctx.send("Turururu")

@bot.command()
async def agendar(ctx):
    await ctx.send("📅 Envie a data e hora do RPG no formato `DD/MM/AAAA HH:MM`:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    try:
        # Leitura da data/hora
        msg_data = await bot.wait_for("message", timeout=60, check=check)
        data_str = msg_data.content.strip()
        new_start = datetime.strptime(data_str, "%d/%m/%Y %H:%M")

        # Checagem de conflitos com eventos existentes
        for key, item in agenda_rpg.items():
            old_start = datetime.strptime(key, "%d/%m/%Y %H:%M")
            old_end = old_start + timedelta(minutes=item["duracao_min"])
            if new_start < old_end and new_end > old_start:
                await ctx.send(
                    f"⚠️ Conflito de horário! Este RPG se sobrepõe ao agendado em `{key}`: **{item['descricao']}**"
                )
                return

        # Antes de seguir, perguntamos duração para já calcular o intervalo completo
        await ctx.send("⏱️ Qual a duração da sessão? Formato `HH:MM`")
        msg_dur = await bot.wait_for("message", timeout=30, check=check)
        h, m = map(int, msg_dur.content.strip().split(":"))
        new_end = new_start + timedelta(hours=h, minutes=m)
        new_dur_min = h * 60 + m

        # Se não houve conflito, seguimos com descrição e cargo
        chave = new_start.strftime("%d/%m/%Y %H:%M")
        await ctx.send("📝 Qual é a descrição da sessão?")
        msg_desc = await bot.wait_for("message", timeout=30, check=check)
        descricao = msg_desc.content.strip()

        await ctx.send("📛 Marque o cargo do RPG (ex: @Aventureiros).")
        msg_cargo = await bot.wait_for("message", timeout=30, check=check)

        if not msg_cargo.role_mentions:
            return await ctx.send("❌ Você precisa mencionar um cargo válido com `@nome_do_cargo`.")

        cargo = msg_cargo.role_mentions[0]

        # Salvar na agenda
        agenda_rpg[chave] = {
            "autor": ctx.author.name,
            "descricao": descricao,
            "cargo_id": cargo.id,
            "canal_id": ctx.channel.id,
            "duracao_min": new_dur_min
        }
        salvar_agenda()
        agendar_notificacoes(new_start, ctx.channel.id, cargo.id, descricao, new_dur_min)

        await ctx.send(
            f"✅ RPG agendado para {chave}, duração {h:02d}:{m:02d}, com cargo {cargo.mention}!"
        )

    except Exception as e:
        await ctx.send("⏰ Tempo esgotado ou erro de formato. Tente novamente.")

# --- Comando para listar com índices ---
@bot.command(name="listar")
async def listar(ctx):
    if not agenda_rpg:
        return await ctx.send("📭 Nenhum RPG agendado.")

    linhas = []
    for i, data_str in enumerate(sorted(agenda_rpg), start=1):
        item = agenda_rpg[data_str]
        linhas.append(f"{i}. `{data_str}` – {item['descricao']}")

    texto = "📋 **Agenda de RPGs (use o número para excluir):**\n" + "\n".join(linhas)
    await ctx.send(texto)

# --- Comando excluir agora aceita índice ou data completa ---
@bot.command(name="excluir")
async def excluir(ctx, arg: str = None):
    if not agenda_rpg:
        return await ctx.send("📭 Nenhum RPG para excluir.")

    keys = sorted(agenda_rpg)

    # Se o usuário passou um número, converte em índice
    if arg and arg.isdigit():
        idx = int(arg) - 1
        if 0 <= idx < len(keys):
            chave = keys[idx]
        else:
            return await ctx.send("❌ Índice inválido.")
    # Se passou uma string não numérica, assume que é a data completa
    elif arg:
        chave = arg.strip()
        if chave not in agenda_rpg:
            return await ctx.send("❌ Não encontrei nenhum RPG nessa data/hora.")
    else:
        # Sem argumento: pede ao usuário
        await ctx.send("🗑️ Digite o número ou a data/hora (DD/MM/AAAA HH:MM) do RPG a excluir:")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for("message", timeout=30, check=check)
            content = msg.content.strip()
            if content.isdigit():
                idx = int(content) - 1
                if 0 <= idx < len(keys):
                    chave = keys[idx]
                else:
                    return await ctx.send("❌ Índice inválido.")
            else:
                chave = content
                if chave not in agenda_rpg:
                    return await ctx.send("❌ Não encontrei nenhum RPG nessa data/hora.")
        except asyncio.TimeoutError:
            return await ctx.send("⏰ Tempo esgotado. Tente de novo.")

    # Se chegou aqui, temos a chave certa
    info = agenda_rpg.pop(chave)
    salvar_agenda()
    await ctx.send(f"✅ RPG de `{chave}` ({info['descricao']}) excluído.")


@bot.command()
async def agendados(ctx):
    if not agenda_rpg:
        await ctx.send("Tragicamente não há nenhum rpg agendado")
        return

    resposta = "📅 **Agenda de RPGs:**\n"
    for data_str in sorted(agenda_rpg):
        item = agenda_rpg[data_str]
        resposta += f"🕒 `{data_str}` - {item['descricao']} \n"
    await ctx.send(resposta)

@bot.command()
async def amaldiçoe(ctx, membro: discord.Member):
    frases = [
        "VOCÊ ACHA MESMO QUE VAI SOBREVIVER A PRÓXIMA SESSÃO? :morra: **_Sons de raio_**",
        "SEU PRÓXIMO d20 SERÁ 1! :morra: **_Sons de raio_**",
        "RESPIRAÇÃO AUTOMÁTICA DESLIGADA :morra: **_Sons de raio_**",
        "QUE SUA CAMISINHA ESTOURE :morra: **_Sons de raio**",
        "QUE SUA RINITE ATAQUE :morra: **_Sons de raio_**",
        ""
    ]

    frase_escolhida = random.choice(frases)
    await ctx.send(f"{membro.mention} – {frase_escolhida}")

@bot.command()
async def xingue(ctx, membro: discord.Member):
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
        "SEU FILHO DA PUTA,VOU COMER SEU CU.ARROMBADO DO CARALHO,SUA MÃE ALUGA A BUCETA PRA COMPRAR FIXADOR DE DENTADURA PRO SEU PAI, AQUELE CORNO BROXA. CHIFRUDO, VOU ENFIAR MEU BRAÇO NO SEU ÂNUS E ARRANCAR SEU INTESTINO. LOGO DEPOIS VOU ENFORCAR SUA AVÓ COM ELE, AQUELA VELHA BISCATE QUE FAZ CROCHÊ PRA FORA EM TROCA DE PICA. SUAS TIAS TÊM PÊLO NO DENTE E SUA IRMÃ TEM POLENGUINHO NA VIRILHA, SEU GRANDE FILHO DA PRÊULA. SUA MÃE DAVA LEITE DA CABEÇA DO PAU DO SEU PAI PRA VOCÊ BEBER, FILHO DA PUTA. ISSO MESMO, VOCÊ TOMAVA MAMADEIRA DE PORRA DESDE CRIANÇA. POR ISSO É O RETARDADO MENTAL QUE É HOJE, SEU ZÉ BEBEDOR DE SUCO DE CARALHO. O PADRE TE BENZEU COM ÁGUA PARADA, HOJE VOCÊ SOFRE OS EFEITOS RETARDADOS DO AEDES AEGYPT QUE SE ALOJA DENTRO DO SEU OUVIDO, SEU MONTE DE ESTERCO. SEU AVÔ ARROMBADO USA FRALDA E TE OBRIGA A LIMPAR OS COCOZUDOS DELE COM UMA COLHER DE DANONINHO, SEU CAPACHO DO CARALHO. SUA MÃE TE FAZ DORMIR COM O REX, AQUELE CHIUAUA FILHO DA PUTA E CHEIO DE SARNA. E DURANTE A MADRUGADA O REX ABUSA SEXUALMENTE DE VOCÊ, ATÓLA A PATINHA DENTRO DESSE SEU CU PELÚDO, SEU FRACASSADO. LEMBRA DA JANDIRA, AQUELA SUA PRIMA MONOTETA ? POIS É, ENFIEI UM TACO DE BASEBALL NO CU DELA. A MÃE DELA DEU O FLAGRANTE NA GENTE E AO INVÉS DE FICAR BRAVA, PEDIU O TACO EMPRESTADO. VADIA DO CARALHO ESSA SUA TIA, SÓ PODE TER APRENDIDO COM SUA MÃE, AQUELA BISCATE. QUE ALIÁS, CONTINUA CHUPANDO O CARALHO DO ZÉ DO PACOTE, O TRAFICANTE QUE MORA AÍ DO LADO DA SUA CASA DE BARRO, SEU FILHO DUMA MACONHEIRA VAGABUNDA",
        "Torcedor do Vasca da Gama"
    ]

    frase_escolhida = random.choice(frases)
    await ctx.send(f"{membro.mention} – {frase_escolhida}")

@bot.command()
async def resumir(ctx, quantidade: int = 50):  # padrão: 50 mensagens
    if not conversa:
        await ctx.send("❌ Não há conversa suficiente para resumir.")
        return

    # Garante que não vá além do número de mensagens disponíveis
    quantidade = min(quantidade, len(conversa))

    mensagens_para_resumir = conversa[-quantidade:]
    texto = "\n".join([f"{msg['autor']}: {msg['conteudo']}" for msg in mensagens_para_resumir])

    prompt = f"Resuma a seguinte conversa entre usuários de Discord:\n\n{texto}"

    resposta = openai.ChatCompletion.create(
        model="gpt-4.1-nano",
        messages=[
            {"role": "system", "content": "Você é um assistente que resume conversas do Discord de forma clara e breve."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    resumo = resposta.choices[0].message.content
    await ctx.send(f"📄 **Resumo das últimas {quantidade} mensagens:**\n{resumo}")



@bot.command()
async def anote(ctx):
    await ctx.send("📝 O que você quer que eu te lembre?")
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        msg_lembrar = await bot.wait_for("message", timeout=60, check=check)
        conteudo = msg_lembrar.content.strip()

        await ctx.send("⏰ Quando? (formato `DD/MM/AAAA HH:MM` ou `diario HH:MM` ou `semanal DIA HH:MM`)\nExemplos:\n`05/08/2025 19:30`\n`diario 08:00`\n`semanal segunda 18:00`")
        msg_quando = await bot.wait_for("message", timeout=60, check=check)
        info = msg_quando.content.lower().strip()

        canal_id = ctx.channel.id
        autor_id = ctx.author.id

        if info.startswith("diario "):
            hora = datetime.strptime(info.split(" ")[1], "%H:%M").time()
            scheduler.add_job(
                lambda: bot.loop.create_task(
                    bot.get_channel(canal_id).send(f"⏰ <@{autor_id}> lembrete diário: {conteudo}")
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
                lambda: bot.loop.create_task(
                    bot.get_channel(canal_id).send(f"📆 <@{autor_id}> lembrete semanal ({dia_semana}): {conteudo}")
                ),
                trigger="cron", day_of_week=dias[dia_semana], hour=hora.hour, minute=hora.minute
            )
            await ctx.send("✅ Ta feito chefia")

        else:
            data = datetime.strptime(info, "%d/%m/%Y %H:%M")
            scheduler.add_job(
                lambda: bot.loop.create_task(
                    bot.get_channel(canal_id).send(f"🔔 <@{autor_id}> lembrete: {conteudo}")
                ),
                trigger="date", run_date=data
            )
            await ctx.send("✅ Ta feito chefia ")

    except Exception as e:
        await ctx.send("❌ Erro ao configurar lembrete. Verifique o formato e tente novamente.")


@bot.command(name="defina")
async def defina(ctx, *, termo: str):
    """
    Gera a definição de um termo em português e um exemplo de uso,
    usando o modelo ChatGPT da OpenAI.
    """

    prompt = (
        f"Você é um dicionário em português. "
        f"Defina de forma clara e concisa a palavra ou expressão “{termo}” "
        f"e apresente um exemplo de uso em uma frase."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "Você é um dicionário em português."},
                {"role": "user",   "content": prompt}
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
        "**Fonte: **"
        ]

        fonte_escolhida = random.choice(text)

        res = conteudo+"\n\n"+fonte_escolhida

        await ctx.send(res)

    except Exception as e:
        # Se houver erro na API ou internet, captura e avisa
        await ctx.send("Karalho brother você escreveu em hieróglifos filho da puta?")
        print(f"[ERRO] defina: {e}")

@bot.command(name="defenda-me")
async def defender(ctx, quantidade: int = 50):
    """
    Pega as últimas 'quantidade' mensagens e gera
    um texto defendendo o ponto de vista do bot.
    """
    # Filtra apenas as mensagens de usuários (não bots) e ignora o próprio comando
    canal = ctx.channel
    mensagens = []
    async for msg in canal.history(limit=quantidade + 10):  # pega um pouco a mais para filtrar
        if msg.author.bot:
            continue
        if msg.id == ctx.message.id:
            continue
        mensagens.append(f"{msg.author.name}: {msg.content}")

    if not mensagens:
        return await ctx.send("é foda, não tenho contexto o bastante para te defender.")

    # Inverte pra ordem cronológica
    mensagens = list(reversed(mensagens))
    conversa_texto = "\n".join(mensagens)

    prompt = (
        "Você é um assistente que sempre defende a posição do “Jarvis Bot” "
        "em qualquer debate. Abaixo está o histórico recente de uma conversa. "
        "Baseado nisso, produza um texto argumentativo coerente e persuasivo, "
        "defendendo o ponto de vista do Jarvis Bot frente aos argumentos apresentados.\n\n"
        f"{conversa_texto}\n\n"
        "Resposta:"
    )

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "Você defende sempre o Jarvis Bot."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=300
        )
        resposta = resp.choices[0].message.content.strip()
        # Envia em um embed para ficar mais elegante
        embed = discord.Embed(
            title="Veja bem, em defesa do meu cliente...",
            description=resposta,
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    except Exception as e:


        await        print(f"[ERRO defender] {e}")
        await ctx.send("puta que pariu, ai tbm nem eu consigo te defender")

@bot.command(name="rankduelos")
async def rank_duelos(ctx):
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

# 🔔 Função que agenda as notificações. Ta mas cade os erros? 
def agendar_notificacoes(data, canal_id, cargo_id, descricao, dur_min):
    horario = data
    aviso = data - timedelta(minutes=15)
    fim = data + timedelta(minutes=dur_min)

    async def enviar_msg(msg_hora):
        canal = bot.get_channel(int(canal_id))
        cargo = discord.utils.get(canal.guild.roles, id=int(cargo_id))
        if canal and cargo:
            await canal.send(f"🔔 {cargo.mention} - {msg_hora} da sessão: **{descricao}**")
        
    async def apagar_evento():
        chave = data.strftime("%d/%m/%Y %H:%M")
        if chave in agenda_rpg:
            del agenda_rpg[chave]
            salvar_agenda()
    
    scheduler.add_job(lambda: bot.loop.create_task(enviar_msg("15 minutinhos ainda")), 'date', run_date=aviso)
    scheduler.add_job(lambda: bot.loop.create_task(enviar_msg("FINALMENTE POHA **SONS DE FOGUETE**")), 'date', run_date=horario)
    scheduler.add_job(lambda: bot.loop.create_task(apagar_evento()), 'date', run_date=fim)

# Retrieve token from the .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
bot.run(os.getenv('DISCORD_TOKEN'))
