import json
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord

# Variáveis globais
conversa = []
scheduler = AsyncIOScheduler()
agenda_rpg = {}
ARQUIVO = "agenda_rpg.json"
ARQUIVO_DUELOS = "duelos.json"

# ===== FUNÇÕES DE AGENDA =====

def carregar_agenda():
    global agenda_rpg
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r") as f:
            agenda_rpg = json.load(f)
    else:
        agenda_rpg = {}
    return agenda_rpg

def salvar_agenda():
    with open(ARQUIVO, "w") as f:
        json.dump(agenda_rpg, f, indent=2)

# ===== FUNÇÕES DE DUELOS =====

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

# ===== FUNÇÕES DE CONVERSA =====

def adicionar_mensagem(autor, conteudo, timestamp):
    global conversa
    conversa.append({
        "autor": autor,
        "conteudo": conteudo,
        "timestamp": timestamp
    })
    
    if len(conversa) > 500:
        conversa.pop(0)

def obter_conversa():
    return conversa

# ===== FUNÇÕES DE NOTIFICAÇÕES =====

def agendar_notificacoes(bot, data, canal_id, cargo_id, descricao, dur_min):
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

def init_scheduler():
    global scheduler
    if not scheduler.running:
        scheduler.start()

def get_scheduler():
    return scheduler
