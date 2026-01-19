from utils import adicionar_mensagem, init_scheduler, carregar_agenda, get_scheduler
from datetime import datetime, timedelta

def register_events(bot):

    @bot.event
    async def on_ready():
        from utils import init_scheduler, carregar_agenda, agendar_notificacoes, get_scheduler
        
        print(f"🤖 Bot online como {bot.user}")
        
        # Inicializa scheduler
        init_scheduler()
        scheduler = get_scheduler()
        
        # Reagendar eventos ao reiniciar
        agenda_rpg = carregar_agenda()
        for chave, item in agenda_rpg.items():
            dt = datetime.strptime(chave, "%d/%m/%Y %H:%M")
            if dt > datetime.now():
                agendar_notificacoes(bot, dt, item["canal_id"], item["cargo_id"], item["descricao"], item["duracao_min"])

    @bot.event
    async def on_message(message):
        """Registra todas as mensagens e processa comandos"""
        if message.author.bot:
            return

        # Adiciona a mensagem ao histórico
        adicionar_mensagem(
            autor=message.author.name,
            conteudo=message.content,
            timestamp=message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )

        # Necessário para não bloquear outros comandos
        await bot.process_commands(message)
